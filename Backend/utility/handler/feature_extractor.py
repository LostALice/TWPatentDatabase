# Code by AkinoAlice@TyrantRey

import numpy as np
import torch
import torchvision.transforms as T  # type: ignore[import-untyped] # noqa: N812

# from PIL import Image
from transformers import AutoFeatureExtractor, AutoImageProcessor, AutoModel  # type: ignore[import-untyped]


class ImageFeatureExtractor:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.model = AutoModel.from_pretrained(model_name)
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.extractor = AutoFeatureExtractor.from_pretrained(model_name)

    def extract_embeddings(self, images: list[np.ndarray]):
        """
        Compute embeddings for a batch of images using the provided model.

        Args:
            images: A list of PIL images.

        Returns:
            A dictionary with a key "embeddings" containing the computed embeddings.

        """
        transformation_chain = T.Compose(
            [
                T.Resize(int((256 / 224) * self.extractor.size["height"])),
                T.CenterCrop(self.extractor.image_size["height"]),
                T.ToTensor(),
                T.Normalize(mean=self.extractor.image_mean, std=self.extractor.image_std),
            ]
        )

        device = self.model.device

        image_batch_transformed = torch.stack([transformation_chain(image) for image in images])

        new_batch = {"pixel_values": image_batch_transformed.to(device)}

        with torch.no_grad():
            embeddings = self.model(**new_batch).last_hidden_state[:, 0].cpu()

        return {"embeddings": embeddings}


if __name__ == "__main__":
    # model_ckpt = "nateraw/vit-base-beans"
    # processor = AutoImageProcessor.from_pretrained(model_ckpt)
    # model = AutoModel.from_pretrained(model_ckpt)

    a = ImageFeatureExtractor("nateraw/vit-base-beans")
