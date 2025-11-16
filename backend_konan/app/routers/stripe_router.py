from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import os
from app.core.security import verify_jwt

try:
    import stripe
except ImportError:
    stripe = None

router = APIRouter(dependencies=[Depends(verify_jwt)])

# =====================================================
# ⚙️ MODE TEST AUTOMATIQUE
# =====================================================
FAKE_MODE = False
stripe_key = os.getenv("STRIPE_SECRET_KEY", "")
if not stripe_key or "FAKE" in stripe_key or stripe is None:
    FAKE_MODE = True

# =====================================================
# 💳 CRÉATION DE SESSION (réelle ou simulée)
# =====================================================
@router.post("/create-checkout-session")
async def create_checkout_session():
    """
    Crée une session Stripe Checkout.
    Si FAKE_MODE = True, renvoie une session simulée sans appel Stripe réel.
    """
    if FAKE_MODE or stripe is None:
        # Simulation locale sans API Stripe
        return JSONResponse(
            content={
                "sessionId": "cs_test_FAKE_SESSION",
                "url": "https://checkout.stripe.fake.local/success",
                "mode": "simulation"
            }
        )

    try:
        stripe.api_key = stripe_key
        domain = os.getenv("FRONTEND_URL", "http://localhost:3000")
        price_id = os.getenv("STRIPE_PRICE_MONTHLY", "price_fake")

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{domain}/success",
            cancel_url=f"{domain}/cancel",
        )
        return JSONResponse(content={"sessionId": session.id, "url": session.url})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur Stripe: {e}")

# =====================================================
# 🧾 WEBHOOK (SIMULÉ)
# =====================================================
@router.post("/webhook")
async def stripe_webhook():
    """
    Simule la réception d'un webhook Stripe.
    """
    if FAKE_MODE:
        return {"status": "fake-webhook-received"}
    return {"status": "webhook-received"}

# =====================================================
# 🔍 VÉRIFICATION DE SESSION (SIMULÉE OU RÉELLE)
# =====================================================
@router.post("/verify-session")
async def verify_session(payload: dict):
    """
    Vérifie le statut d'une session Checkout.
    Expects JSON body: {"sessionId": "cs_test_xxx"}
    - En FAKE_MODE renvoie un statut simulé.
    - En mode réel interroge Stripe.
    """
    session_id = payload.get("sessionId")
    if not session_id:
        raise HTTPException(status_code=422, detail="sessionId manquant dans le payload")

    # Simulation locale
    if FAKE_MODE:
        sid = session_id.upper()
        if "FAKE" in sid or sid.startswith("CS_TEST"):
            return JSONResponse(content={"sessionId": session_id, "status": "completed", "paid": True})
        if "PENDING" in sid:
            return JSONResponse(content={"sessionId": session_id, "status": "pending", "paid": False})
        if "CANCEL" in sid:
            return JSONResponse(content={"sessionId": session_id, "status": "canceled", "paid": False})
        return JSONResponse(content={"sessionId": session_id, "status": "unknown", "paid": False})

    # Mode réel
    try:
        stripe.api_key = stripe_key
        session = stripe.checkout.Session.retrieve(session_id)
        payment_status = session.get("payment_status")  # 'paid' ou 'unpaid'
        return JSONResponse(
            content={
                "sessionId": session_id,
                "status": session.get("status", "unknown"),
                "payment_status": payment_status,
                "paid": payment_status == "paid",
                "customer": session.get("customer"),
            }
        )
    except stripe.error.InvalidRequestError as e:
        raise HTTPException(status_code=404, detail=f"Stripe session not found: {e.user_message if hasattr(e, 'user_message') else str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur vérification session Stripe: {str(e)}")
