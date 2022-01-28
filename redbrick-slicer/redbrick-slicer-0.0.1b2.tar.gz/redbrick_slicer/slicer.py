"""Main object for RedBrick SDK."""
import os
import json
import time
import gzip
from datetime import datetime
from configparser import ConfigParser
from typing import Dict, List, Optional, Tuple, no_type_check
from uuid import uuid4

# import qt
import slicer
from DICOMLib import DICOMUtils

from redbrick_slicer.common.context import RBContext
from redbrick_slicer.project import RBProject
from redbrick_slicer.utils.files import download_files


# pylint: skip-file


# class RedBrickLogin(qt.QWidget):
#     """RedBrick login form using Qt."""

#     def __init__(self) -> None:
#         """Initialize the login form."""
#         super().__init__()
#         flo = qt.QFormLayout()
#         self.submitted = False

#         self.username = qt.QLineEdit()
#         self.username.textChanged.connect(self.text_changed)
#         flo.addRow("Username:", self.username)

#         self.password = qt.QLineEdit()
#         self.password.setEchoMode(qt.QLineEdit.Password)
#         self.password.textChanged.connect(self.text_changed)
#         flo.addRow("Password:", self.password)

#         self.login = qt.QPushButton("Login")
#         self.login.clicked.connect(self.button_clicked)
#         self.login.resize(60, 30)
#         self.login.setEnabled(False)
#         flo.addRow(self.login)

#         self.setLayout(flo)
#         self.setWindowTitle("RedBrick AI Login")
#         self.setMinimumSize(400, 80)
#         self.show()

#     def text_changed(self) -> None:
#         """Text field change event handler."""
#         self.login.setEnabled(bool(self.username.text and self.password.text))

#     def button_clicked(self) -> None:
#         """Button click event handler."""
#         self.submitted = True
#         self.close()


class RBSlicer:
    """Interact with a RedBrick task in 3D Slicer application."""

    def __init__(
        self,
        context: RBContext,
        username: str,
        password: str,
        client_id: str,
        url: str,
        region: str,
    ) -> None:
        """Construct RBProject."""
        self.context = context
        self.region = region
        self.client_id = client_id
        self.url = url

        self.username = username
        self.password = password

        self.auth_token: Optional[str] = None
        self.project: Optional[RBProject] = None

        self.segments: List[str] = []

        self.root = os.path.join(os.path.expanduser("~"), ".redbrick-slicer")
        self.org_dir = ""
        self.project_dir = ""
        self.task_dir = ""

        self.data_dir = ""

    def authenticate_user(self) -> str:
        """Authenticate user and get username and auth token."""
        import boto3  # type: ignore

        # config_file = os.path.join(os.path.expanduser("~"), ".redbrickai", "token")
        # config = ConfigParser()
        # config.read(config_file)
        # if (
        #     "token" in config
        #     and "uname" in config["token"]
        #     and "value" in config["token"]
        #     and "time" in config["token"]
        #     and int(config["token"]["time"]) >= int(datetime.now().timestamp()) + 9000
        # ):
        #     return config["token"]["uname"], config["token"]["value"]

        client = boto3.client("cognito-idp", region_name=self.region)

        # login_form = RedBrickLogin()
        # while not login_form.submitted:
        #     time.sleep(1)
        # username = login_form.username.text
        # password = login_form.password.text
        # login_form.delete()

        # print("RedBrick Login")
        # username = input("Username: ").strip()
        # password = input("Password: ").strip()

        response = client.initiate_auth(
            ClientId=self.client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": self.username, "PASSWORD": self.password},
        )
        assert (
            response["ResponseMetadata"]["HTTPStatusCode"] == 200
            and response["AuthenticationResult"]["AccessToken"]
        )
        return response["AuthenticationResult"]["AccessToken"]

        # config["token"] = {
        #     "uname": password,
        #     "time": int(datetime.now().timestamp())
        #     + response["AuthenticationResult"]["ExpiresIn"],
        #     "value": response["AuthenticationResult"]["AccessToken"],
        # }

        # os.makedirs(os.path.dirname(config_file), exist_ok=True)
        # with open(config_file, "w", encoding="utf-8") as file_:
        #     config.write(file_)

    def logout(self) -> None:
        """Logout current session and delete token file."""
        config_file = os.path.join(os.path.expanduser("~"), ".redbrickai", "token")
        if os.path.isfile(config_file):
            os.remove(config_file)
        self.username = None
        self.auth_token = None

    @staticmethod
    def _get_categories(category: Dict) -> List[str]:
        category_names = [category["name"]]
        for child in category.get("children", []):
            category_names += [
                category_names[0] + "::" + name
                for name in RBSlicer._get_categories(child)
            ]
        return category_names

    @no_type_check
    def get_task(
        self, org_id: str, project_id: str, task_id: str, stage_name: str
    ) -> None:
        """Get task for labeling."""
        try:
            self.auth_token = self.authenticate_user()
        except Exception:
            print("Error signing in (Invalid username or password).")
            return

        self.context.client.auth_token = self.auth_token

        if not self.project:
            self.project = RBProject(self.context, org_id, project_id)

        task, taxonomy = self.project.export.get_raw_data_single(task_id)

        parent_cat = taxonomy.get("categories", [])
        if len(parent_cat) == 1 and parent_cat[0]["name"] == "object":
            for child in parent_cat[0]["children"]:
                self.segments += RBSlicer._get_categories(child)

        print("Available categories:", self.segments)

        slicer.mrmlScene.Clear(0)

        self.org_dir = os.path.join(self.root, str(org_id))
        self.project_dir = os.path.join(self.org_dir, str(project_id))
        self.task_dir = os.path.join(self.project_dir, str(task_id))

        self.data_dir = os.path.join(self.task_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)

        files = []
        for idx, item in enumerate(task["itemsPresigned"]):
            path = os.path.join(self.data_dir, f"{idx}.dcm")
            if not os.path.isfile(path):
                files.append((item, path))

        download_files(files)

        with DICOMUtils.TemporaryDICOMDatabase() as db:
            DICOMUtils.importDicom(self.data_dir, db)
            patientUIDs = db.patients()
            assert len(patientUIDs) == 1, "Failed to load data"
            DICOMUtils.loadPatientByUID(patientUIDs[0])

        if task["labelsPath"]:
            labels_path = os.path.join(self.task_dir, "labels.nii")
            if os.path.isfile(labels_path):
                os.remove(labels_path)
            download_files([(task["labelsPath"], labels_path)])
            slicer.util.loadSegmentation(labels_path)
            segmentationNode = slicer.mrmlScene.GetFirstNodeByClass(
                "vtkMRMLSegmentationNode"
            )

        else:
            segmentationNode = slicer.vtkMRMLSegmentationNode()
            slicer.mrmlScene.AddNode(segmentationNode)

        slicer.util.selectModule("SegmentEditor")
        segmentationNode = slicer.mrmlScene.GetFirstNodeByClass(
            "vtkMRMLSegmentationNode"
        )

        rb_segmentation = segmentationNode.GetSegmentation()
        labels = task["labels"]
        label_rb_map = {}
        for label in labels:
            label_rb_map[label["dicom"]["instanceid"]] = "::".join(
                label["category"][0][1:]
            )

        display = segmentationNode.GetDisplayNode()
        for num in range(rb_segmentation.GetNumberOfSegments()):
            seg = rb_segmentation.GetNthSegment(num)
            display.SetSegmentVisibility(rb_segmentation.GetNthSegmentID(num), True)
            val = seg.GetLabelValue()
            if val in label_rb_map:
                seg.SetName(label_rb_map[val])

        self.project.labeling.assign_task(stage_name, task_id, self.username)

        while True:
            user_val = input("Enter:\n1. Save\n2. Submit\n3. Exit\n\n").strip()

            if user_val == "1":
                self.save_data(task_id, stage_name, False)
                print("Saved")
            elif user_val == "2":
                self.save_data(task_id, stage_name, True)
                print("Submitted")
                break
            else:
                slicer.mrmlScene.Clear(0)
                break

    @no_type_check
    def save_data(
        self,
        task_id: str,
        stage_name: str,
        finished: bool = False,
    ) -> None:
        """Save data for task."""
        import numpy as np
        import nibabel as nb  # type: ignore

        scene = slicer.mrmlScene

        segmentationNode = scene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
        rb_segmentation = segmentationNode.GetSegmentation()
        labels = []
        for num in range(rb_segmentation.GetNumberOfSegments()):
            seg = rb_segmentation.GetNthSegment(num)
            name = seg.GetName()
            if name not in self.segments:
                print(f"Category: `{name}` not found. Skipping")
                return
            labels.append(
                {
                    "category": [["object"] + name.split("::")],
                    "attributes": [],
                    "labelid": str(uuid4()),
                    "dicom": {"instanceid": seg.GetLabelValue()},
                }
            )

        segmentationNode = scene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
        referenceVolumeNode = scene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
        labelmapVolumeNode = scene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
        slicer.modules.segmentations.logic().ExportVisibleSegmentsToLabelmapNode(
            segmentationNode, labelmapVolumeNode, referenceVolumeNode
        )
        new_labels = os.path.join(self.task_dir, "new_labels.nii")
        slicer.util.saveNode(labelmapVolumeNode, new_labels)
        scene.RemoveNode(labelmapVolumeNode.GetDisplayNode().GetColorNode())
        scene.RemoveNode(labelmapVolumeNode)

        img = nb.load(new_labels)
        img.set_data_dtype(np.ubyte)
        data = np.round(img.get_fdata()).astype(np.ubyte)
        means = nb.Nifti1Image(data, header=img.header, affine=img.affine)
        new_labels = os.path.join(self.task_dir, "new_labels_converted.nii")
        nb.save(means, new_labels)
        with open(new_labels, "rb") as file_:
            compressed = gzip.compress(file_.read())

        self.project.labeling.put_task(
            stage_name,
            {
                "taskId": task_id,
                "labelBlob": compressed,
                "draft": not finished,
                "labels": labels,
            },
        )

        if finished:
            scene.Clear(0)
