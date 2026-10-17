import io
import os


def _client():
    import oci

    config = {
        "user": os.environ["OCI_USER"],
        "fingerprint": os.environ["OCI_FINGERPRINT"],
        "tenancy": os.environ["OCI_TENANCY"],
        "region": os.environ.get("OCI_REGION", "us-sanjose-1"),
    }
    key_content = os.environ.get("OCI_PRIVATE_KEY")
    if key_content:
        config["key_content"] = key_content.replace("\\n", "\n")
    else:
        config["key_file"] = os.environ["OCI_KEY_FILE"]
    pass_phrase = os.environ.get("OCI_KEY_PASSPHRASE")
    if pass_phrase:
        config["pass_phrase"] = pass_phrase
    oci.config.validate_config(config)
    return oci.object_storage.ObjectStorageClient(config)


def put_object(object_key, content, content_type):
    client = _client()
    return client.put_object(
        os.environ["OCI_NAMESPACE"],
        os.environ["OCI_BUCKET"],
        object_key,
        content,
        content_type=content_type,
    )


def get_object(object_key):
    response = _client().get_object(
        os.environ["OCI_NAMESPACE"], os.environ["OCI_BUCKET"], object_key
    )
    return io.BytesIO(response.data.content)


def delete_object(object_key):
    return _client().delete_object(
        os.environ["OCI_NAMESPACE"], os.environ["OCI_BUCKET"], object_key
    )

