# Code by AkinoAlice@TyrantRey

from PIL import Image
from transformers import CLIPModel, CLIPProcessor

from Backend.utility.handler.log_handler import Logger


class ImageEmbedding:
    def __init__(self):
        self.logger = Logger().get_logger()
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
        self.model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")

    def process(self, image_path: str) -> list[float]:
        """
        Process the image and return its embedding using CLIP model.
        """
        self.logger.info("Processing image: %s", image_path)
        _image = Image.open(image_path)
        inputs = self.processor(images=_image, return_tensors="pt")
        feature = self.model.get_image_features(**inputs)

        return feature.detach().cpu().numpy()[0].tolist()


# class TextEmbedding:
#     def __init__(self):
#         self.logger = Logger().get_logger()
#         self.model = SentenceTransformer("nomic-ai/nomic-embed-text-v2-moe", trust_remote_code=True)

#     def process(self, text: str) -> np.ndarray:
#         """
#         Process the image and return its embedding using nomic-embed-text-v2-moe model.
#         """
#         self.logger.info("Processing sentences: %s", text)

#         return self.model.encode(text)


if __name__ == "__main__":
    image_embedding = ImageEmbedding()
    image_embedding_result = image_embedding.process("./test/image/test.png")
    # (768, )
    print(image_embedding_result)  # noqa: T201

    # text_embedding = TextEmbedding()
    # text_embedding_result = text_embedding.process("Your sentence to embed.")
    # # (768, )
    # print(text_embedding_result)
    # print(text_embedding_result.shape)
