export const endpoints = {
    login: "/auth/login", // {email, password} -> {access_token}
    register: "/auth/register", // {email, password, name}
    me: "/auth/me", // GET -> profil si JWT valide
    billingStatus: "/billing/status", // GET -> { plan: "FREE"|"PREMIUM" }
    billingSheet: "/billing/payment-sheet", // POST -> { paymentIntent, ephemeralKey, customer, publishableKey }
    };