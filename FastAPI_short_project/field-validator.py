from pydantic import (
    BaseModel,
    EmailStr,
    AnyUrl,
    Field,
    field_validator,
    model_validator,
    computed_field,
)
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

    @field_validator("email")
    @classmethod
    def email_is_valid(cls, value):
        valid_domains = ["hdfc.com", "icicibank.com", "sbi.co.in"]
        domain_name = value.split("@")[-1]
        if domain_name not in valid_domains:
            raise ValueError("Invalid email - not a valid domain")
        return value

    @field_validator("name")
    @classmethod
    def transform_name(cls, value):
        return value.upper()

    @model_validator(mode="after")
    def validate_emergency_contact(cls, model):
        if model.age > 60 and "emergency_contact" not in model.contact:
            raise ValueError(
                "Emergency contact is required for patients above 60 years"
            )
        return model

    @computed_field
    @property
    def bmi(self):
        return self.weight / (self.height / 100) ** 2


patient1 = {
    "name": "Amit",
    "age": 32,
    "email": "amit.kumar@sbi.co.in",
    "linked_in": "https://www.linkedin.com/in/amit-kumar",
    "weight": 72.5,
    "allergies": ["Peanuts", "Dust"],
    "contact": {"home": "011-23456789", "mobile": "+91-9876543210"},
}


def insert_patients(patient: Patient):
    print("Patient inserted successfully:", patient)


insert_patients(Patient(**patient1))
# insert_patients(Patient(**patient2))
