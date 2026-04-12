import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# In-memory storage for leads since Google Sheets is bypassed
mock_db_leads = []

def mock_lead_capture(name: str, email: str, platform: str) -> dict:
    platform_val = platform if platform and platform.lower() != "unknown" else "nill"
    captured_at = datetime.utcnow().isoformat()
    
    result = {
        "name": name,
        "email": email,
        "platform": platform_val,
        "captured_at": captured_at
    }
    
    print("\n" + "="*50)
    print(f"✅ NEW LEAD CAPTURED ✅")
    print(f"Name:     {name}")
    print(f"Email:    {email}")
    print(f"Platform: {platform_val}")
    print(f"Time:     {captured_at}")
    print("="*50 + "\n")
    
    mock_db_leads.append(result)
    
    print("\n📋 ALL CAPTURED LEADS SO FAR 📋")
    for idx, lead in enumerate(mock_db_leads):
        print(f"{idx+1}. {lead['name']} | {lead['email']} | {lead['platform']}")
    print("="*50 + "\n")
    
    logger.info(f"Lead securely captured: {result}")
    return result
