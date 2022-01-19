from uuid import uuid4
from typing import Union, Tuple, List
from pathlib import Path

import pendulum
import pandas as pd
import random
from tqdm import tqdm
from fhir.resources.reference import Reference
from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName


class PatientGenerator:
    def __init__(self,
                 n: int,
                 age_range: Tuple[int, int] = None,
                 gender_distribution: Tuple[float, float, float, float] = None,
                 organisation: Reference = None,
                 generate_ids: bool = False):
        self.resource_type = Patient
        self.n = n
        self.age_range = age_range
        self.gender_distribution = gender_distribution
        self._birthdate_range = None
        self.organisation = organisation
        self.generate_ids = generate_ids
        self.resources = None

    def generate(self, display: bool = False, references: bool = False):
        patients = self._generate(display=display)
        self.resources = patients

        if references and not self.generate_ids:
            raise ValueError("Cannot generate references without generating ids")
        elif references:
            return patients, self._generate_references()

        return patients

    def _generate(self, display: bool = False):
        patients = []
        names = self._generate_patient_names(self.n)
        for i in tqdm(range(self.n), desc=f"Generating {self.n} patients", disable=not display):
            patient = self._generate_patient_data(name=names[i])
            patients.append(patient)
        return patients

    def _generate_patient_data(self, name: Tuple[str, str]) -> Patient:

        first_name, last_name = name
        gender = random.choices(
            ["male", "female", "other", "unknown"],
            weights=self.gender_distribution if self.gender_distribution else [0.45, 0.45, 0.1, 0.0], k=1)[0]

        name = HumanName(**{"family": last_name, "given": [first_name]})

        birthdate = self._generate_birthdate()
        patient_dict = {
            "gender": gender,
            "name": [name],
            "birthDate": birthdate
        }
        if self.organisation:
            patient_dict["managingOrganization"] = self.organisation

        if self.generate_ids:
            patient_id = str(uuid4())
            patient_dict["id"] = patient_id

        return Patient(**patient_dict)

    @staticmethod
    def _generate_patient_names(n: int):

        p = Path(__file__).parent.joinpath("data").joinpath("first_names.txt")
        with open(p, "rb") as fnf:
            first_name_list = [fn.decode().strip().capitalize() for fn in fnf.readlines()]
        p = Path(__file__).parent.joinpath("data").joinpath("last_names.txt")
        with open(p, "rb") as lnf:
            last_name_list = [ln.decode().strip().capitalize() for ln in lnf.readlines()]

        first_names = random.choices(first_name_list, k=n)
        last_names = random.choices(last_name_list, k=n)
        names = list(zip(first_names, last_names))

        return names

    def _generate_birthdate(self):
        if not self._birthdate_range:
            if self.age_range:
                if isinstance(self.age_range[0], int):
                    # generate age range from 18-101 years old
                    now = pendulum.now()
                    youngest = pd.to_datetime((now - pendulum.duration(years=self.age_range[0])).to_date_string())
                    oldest = pd.to_datetime((now - pendulum.duration(years=self.age_range[1])).to_date_string())
                else:
                    raise ValueError(f"Unsupported type ({type(self.age_range[0])}) for generating patient ages."
                                     f"Only integers are supported.")
            else:
                # generate age range from 18-101 years old
                now = pendulum.now()
                youngest = pd.to_datetime((now - pendulum.duration(years=18)).to_date_string())
                oldest = pd.to_datetime((now - pendulum.duration(years=101)).to_date_string())

            self._birthdate_range = pd.date_range(oldest, youngest, freq="D").strftime('%Y-%m-%d').tolist()

        birthdate = random.choice(self._birthdate_range)
        return birthdate

    def _generate_references(self) -> List[Reference]:
        return [Reference(reference=f"Patient/{patient.id}") for patient in self.resources]

# class PatientResourceGenerator:
#
#     def __init__(self, resource_generator: FhirResourceGenerator = None,
#                  patients: Union[List[Patient], List[str], bool] = None,
#                  n_per_patient: int = 1):
#         self.patients = patients
#         self.n_per_patients = n_per_patient
#         self.resource_generator = resource_generator
#         self.n = self.resource_generator.n
#         self.resources = None
#
#     def generate(self, patients=None, out_dir: str = None, filename: str = None, generate_ids: bool = False):
#         if patients is None and self.patients is None:
#             raise ValueError("No patients given to generate Resources for.")
#         else:
#             self.patients = patients
#             # TODO use self patients and serialize newly generated patients to list
#             self.resources = self.resource_generator.generate(generate_ids=generate_ids)
#             self.update_with_patient_ids()
#             if filename:
#                 if out_dir:
#                     output_path = os.path.join(out_dir, filename)
#                 else:
#                     output_path = filename
#                 with open(output_path, "w") as outputbundle:
#                     bundle = self.resource_generator.make_bundle()
#                     outputbundle.write(bundle.json(indent=2))
#
#         return self.resources, self.resource_generator.make_bundle()
#
#     def generate_patients(self, bundle=True):
#         n_patients = math.ceil(float(self.n) / self.n_per_patients)
#         patient_generator = PatientGenerator(n=n_patients)
#         patients = patient_generator.generate()
#         if bundle:
#             return patient_generator.make_bundle()
#         else:
#             return patients
#
#     def update_with_patient_ids(self):
#         # Step with n per patient
#         for index in range(0, len(self.resources), self.n_per_patients):
#             patient_resources = self.resources[index: index + self.n_per_patients]
#             for resource in patient_resources:
#                 resource.patient = {
#                     "reference": self.patients[int(index / self.n_per_patients)],
#                     "type": "Patient"
#                 }
#
#         print(self.resources)
