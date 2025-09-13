from pydantic import BaseModel, EmailStr, AnyUrl, Field, field_validator
from typing import List, Dict, Optional, Annotated


class Patient(BaseModel):
    name: Annotated[
        str,
        Field(
            max_length=50,
            title="Name of patient",
            description="Name of patient in less than 50 characters ",
            examples=["Nitish", "Amit"],
        ),
    ]
    age: int = Field(gt=0, lt=120)
    email: EmailStr
    linked_in: AnyUrl
    weight: Annotated[float, Field(gt=0, lt=300, strict=True)]
    married: Annotated[bool, Field(default=None, description="Is the patient married?")]
    allergies: Annotated[
        Optional[List[str]], Field(default=None, max_length=5)
    ]  # you cannot directly write List here, you have to write List[str]
    contact: Dict[
        str, str
    ]  # you cannot directly write Dict here, you have to write Dict[str,str]


patient1 = {
    "name": "John Doe",
    "age": 25,
    "weight": 80.0,
    "married": True,
    "contact": {"email": "lN2Hg@example.com", "phone": "123-456-7890"},
}


def insert_patients(patient: Patient):
    print("Patient inserted successfully:", patient)


insert_patients(Patient(**patient1))
# insert_patients(Patient(**patient2))
