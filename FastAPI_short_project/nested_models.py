from pydantic import BaseModel
from typing import List, Dict, Optional, Annotated


class address(BaseModel):
    city: str
    state: str
    pincode: int


class Patient(BaseModel):
    name: str
    gender: str = "Male"
    age: int
    address: address


address_dict = {"city": "New York", "state": "New York", "pincode": 10001}

address1 = address(**address_dict)

Patient_dict = {"name": "Amit", "age": 32, "address": address1}

Patient1 = Patient(**Patient_dict)

print(Patient1)

# print(Patient1.address.)


# temp=Patient1.model_dump()
# print(temp)

# temp1=Patient1.model_dump_json()
# print(temp1)

# temp2=Patient1.model_dump_json(include={'address':['city']})
# print(temp2)

temp2 = Patient1.model_dump_json(exclude_unset=True)
print(temp2)
