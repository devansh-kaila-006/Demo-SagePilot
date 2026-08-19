def check_refund_permission(amount: float) -> bool:
    """
    Checks if a refund amount requires approval.
    Returns True if auto-approved, False if requires manual escalation.
    """
    # Refund limit for auto-approval is ₹2000
    THRESHOLD = 2000.0
    return amount <= THRESHOLD
