# ============================================
# app/api/laws_ws.py — WebSocket notifications temps réel (Konan Pro Premium)
# ============================================
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

router = APIRouter(prefix="/ws", tags=["WebSocket Notifications"])

# Liste des connexions actives
active_connections: list[WebSocket] = []

async def broadcast_notification(message: dict):
    """Diffuse un message à tous les clients connectés."""
    disconnected = []
    for conn in active_connections:
        try:
            await conn.send_text(json.dumps(message, ensure_ascii=False))
        except Exception:
            disconnected.append(conn)
    # Nettoyage des connexions mortes
    for conn in disconnected:
        active_connections.remove(conn)

@router.websocket("/notifications")
async def websocket_notifications(websocket: WebSocket):
    """Connexion temps réel pour les notifications Pro."""
    await websocket.accept()
    active_connections.append(websocket)
    print(f"Nouveau client connecte ({len(active_connections)} actifs)")

    try:
        while True:
            await websocket.receive_text()  # Ping client (non utilisé)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"Client deconnecte ({len(active_connections)} restants)")
