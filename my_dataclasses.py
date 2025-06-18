from dataclasses import dataclass, field

__all__ = ["NumberData", "AccountData"]


@dataclass
class NumberData:
    number: str = '000-000-0000'
    account_id: list = field(default_factory=list)
    calls: str = '0'
    minutes: str = '0.0'
    total_cost: str = '$0.00'


@dataclass
class AccountData:
    desc: str = 'None'
    account_id: str = '00000000'
    invoice_number: str = '00000000'
    calls: str = '0'
    minutes: str = '0.0'
    total_cost: str = '$0.00'
