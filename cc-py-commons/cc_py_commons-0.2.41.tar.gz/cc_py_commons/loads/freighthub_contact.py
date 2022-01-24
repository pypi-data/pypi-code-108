from dataclasses import dataclass, field

@dataclass
class FreightHubContact:

    contact_name: str = field(default=None)
    contact_phone: str = field(default=None)
    contact_fax: str = field(default=None)
    contact_email: str = field(default=None)
    company_name: str = field(default=None)
    user_id: str = field(default=None)