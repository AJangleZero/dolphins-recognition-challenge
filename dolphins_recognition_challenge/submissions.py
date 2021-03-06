# AUTOGENERATED! DO NOT EDIT! File to edit: notebooks/03_Submissions.ipynb (unless otherwise specified).

__all__ = ['submit_model']

# Cell

from pathlib import Path

# Internal Cell

import json
import requests
import base64
from datetime import datetime
import boto3


import tempfile
from zipfile import ZipFile
import torch
import csv
import pandas as pd

from .datasets import get_dataset
from .instance_segmentation.model import iou_metric

# Internal Cell


def get_presigned_url_from_aws(
    path: Path,
    gateway_url: str = "https://1nxt4cd0y2.execute-api.eu-central-1.amazonaws.com/v1/submission",
):
    r = requests.post(gateway_url, params={"filename": path.name})

    assert r.status_code < 300, f"ERROR ({r.status_code}): {r.text}"

    presigned_url = json.loads(r.text)

    return presigned_url

# Internal Cell

def upload_with_presigned_url(
    presigned_url,
    path,
):
    files = {"file": open(path, "rb")}
    r = requests.post(presigned_url["url"], files=files, data=presigned_url["fields"])

    assert r.status_code < 300, f"ERROR: {r.text}"
#     print(f"OK: {r.text}")

# Cell


def submit_model(model, *, alias: str, name: str, email: str) -> None:
    """Run evaluation on the model using validation dataset and submits the result under name/email to the central server.

    The leaderbord will be updated every few days because it requires all submitted models to be veried and tested independantly.
    """

    if alias == "dupin123":
        raise ValueError("Please change default alias to your own")

    if email == "name.surname@gmail.com":
        raise ValueError("Please change default email to your own")

    # evaluate model and save metrics
    _, data_loader_test = get_dataset("segmentation", batch_size=4)
    iou, iou_df = iou_metric(model, data_loader_test.dataset)

    # submission info
    info = pd.Series(
        dict(alias=alias, name=name, email=email, iou=iou),
        name="info",
    ).to_frame()

    # paths
    ts = datetime.now().isoformat()
    submission_name = f"submission-iou={iou:.5f}-{alias}-{email}-{ts}"
    d = Path(submission_name)
    d.mkdir(exist_ok=True, parents=True)

    model_save_path = d / "model.pt"
    metrics_save_path = d / "metrics.csv"
    info_save_path = d / "info.csv"

    # save everything
    torch.save(model, model_save_path)
    iou_df.to_csv(metrics_save_path)
    info.to_csv(info_save_path)

    # zip it
    zip_fname = Path(submission_name + ".zip")
    with ZipFile(zip_fname, "w") as myzip:
        for f in d.glob("*"):
            myzip.write(f)

    #
    presigned_url = get_presigned_url_from_aws(
        path=zip_fname,
        gateway_url="https://1nxt4cd0y2.execute-api.eu-central-1.amazonaws.com/v1/submission",
    )

    upload_with_presigned_url(presigned_url, zip_fname)

    return zip_fname