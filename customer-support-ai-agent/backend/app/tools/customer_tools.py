"""Customer lookup tool. In production this would call a CRM service."""
from sqlalchemy.orm import Session

from app.models.user import User


def get_customer_details(db: Session, customer_id: str) -> dict:
    """
    Return non-sensitive customer info only.
    SECURITY: never return hashed_password or other secrets to the LLM —
    anything returned here can end up echoed back in a response.
    """
    user = db.query(User).filter(User.id == customer_id).first()
    if not user:
        return {"found": False, "error": "Customer not found"}
    return {
        "found": True,
        "full_name": user.full_name,
        "email_masked": _mask_email(user.email),
        "is_active": user.is_active,
    }


def _mask_email(email: str) -> str:
    try:
        name, domain = email.split("@")
        visible = name[:2]
        return f"{visible}{'*' * max(len(name) - 2, 1)}@{domain}"
    except ValueError:
        return "***"
