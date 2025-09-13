from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Optional, Literal
import json

app = FastAPI()


class Patient(BaseModel):
    id: Annotated[
        str, Field(..., description="This is the id of the patient", example="P001")
    ]
    name: Annotated[
        str, Field(..., description="This is the name of the patient", example="Nitish")
    ]
    city: Annotated[
        str,
        Field(..., description="This is the city of the patient", example="New York"),
    ]
    age: Annotated[
        int,
        Field(
            ...,
            gt=0,
            lt=120,
            description="This is the age of the patient",
            example="34",
        ),
    ]
    gender: Annotated[
        str, Field(..., description="This is the gender of the patient", example="Male")
    ]
    height: Annotated[
        float,
        Field(
            ...,
            gt=0,
            lt=300,
            description="This is the height of the patient in metres ",
            example="165",
        ),
    ]
    weight: Annotated[
        float,
        Field(
            ...,
            gt=0,
            lt=300,
            description="This is the weight of the patient in kgs",
            example="78",
        ),
    ]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height / 100) ** 2, 2)

    @computed_field
    @property
    def verdict(self) -> str:
        return "Obese" if self.bmi > 30 else "Not Obese"


# since we don't have a db as of now so we use a json file to mimic a db
def laod_data():
    with open("Patients.json", "r") as f:
        data = json.load(f)
    return data


def save_data(data):
    with open("Patients.json", "w") as f:
        json.dump(data, f)


@app.get("/")
async def root():
    return {"message": "Hello and welcome to patient management system"}


@app.get("/view_patients")
async def get_patients():
    data = laod_data()
    return data


# now let us say the user wants to view a particular patient
@app.get("/view_patients/{patient_id}")
async def get_patient(
    patient_id: str = Path(
        ...,
        description="This is a patient id of the patient you want to view details of ",
        example="P001",
    )
):
    data = laod_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")


@app.get("/sort")
async def sort(
    sort_by: str = Query(
        ...,
        description="This is the field by which you want to sort the data",
        example="bmi",
    ),
    order: str = Query(
        "asc",
        description="This is the order by which you want to sort the data",
        example="asc",
    ),
):

    valid_fields = ["bmi", "height", "weight"]

    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400, detail=f"Invalid sort_by field, sort by {valid_fields}"
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400, detail=f"Invalid order, order should be asc or desc"
        )

    data = laod_data()

    sorted_data = sorted(
        data.items(), key=lambda x: x[1][sort_by], reverse=order == "desc"
    )
    sorted_dict = dict(sorted_data)

    return sorted_dict


@app.post("/create")
def create(patient: Patient):
    data = laod_data()
    if patient.id in data:
        raise HTTPException(status_code=400, detail="this id already exists")
    # now the patient object is a pydantic object but the data is in json so we also convert the pydantic object into json while storing

    data[patient.id] = patient.model_dump(exclude=["id"])
    save_data(data)
    return JSONResponse(
        status_code=201, content={"message": "Patient created successfully"}
    )


# now , we will define a route that will update a patient. in that case the issue is that for the existing patient model , all the fields are marked manadotry which is not the case here bacause updation does not mean user wants to change all the fields . so we need to make the fields optional in a new model.
class PatientUpdate(BaseModel):
    name: Annotated[
        Optional[str],
        Field(description="This is the name of the patient", example="Nitish"),
    ]
    city: Annotated[
        Optional[str],
        Field(description="This is the city of the patient", example="New York"),
    ]
    age: Annotated[
        Optional[int],
        Field(gt=0, lt=120, description="This is the age of the patient", example="34"),
    ]
    gender: Annotated[
        Optional[Literal["male", "female"]],
        Field(description="This is the gender of the patient", example="Male"),
    ]
    height: Annotated[
        Optional[float],
        Field(
            gt=0,
            lt=300,
            description="This is the height of the patient in metres ",
            example="165",
        ),
    ]
    weight: Annotated[
        Optional[float],
        Field(
            gt=0,
            lt=300,
            description="This is the weight of the patient in kgs",
            example="78",
        ),
    ]


@app.put("/edit/{patient_id}")
def update_patient(patient_id: str, patient_update: PatientUpdate):
    data = laod_data()
    # now this data must be checked for the given id
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    # now extract the existing record of that existing patient
    existing_info = data[patient_id]

    # also get the data of the update records given by user
    update_records = patient_update.model_dump(
        exclude_unset=True
    )  # this is exported as a dict now with only those fields that are to be updated as given by user

    # the values get updated in old records
    for key, value in update_records.items():
        existing_info[key] = value

    # Problem -> value of computed fields also might change , so we need to update that too . So make this into an object of previous patient model. The fields will auto get calculated and updated
    # but 'id' is missing in the new record so add that field first  - now here onwards , all is logical manipulation

    existing_info["id"] = patient_id
    original_object = Patient(**existing_info)
    # now again cnvert this into the form suitable for storing in the json file.
    existing_info = original_object.model_dump(exclude="id")
    data[patient_id] = existing_info

    save_data(data)

    return JSONResponse(status_code=200, content={"message": "Updation successful"})


@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    data = laod_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="No such patient found")
    del data[patient_id]
    save_data(data)

    return JSONResponse(status_code=200, content={"messsage": "deletion successfull"})
