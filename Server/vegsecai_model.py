from PIL import Image
from transformers import AutoTokenizer
from moondream.hf import LATEST_REVISION, Moondream, detect_device

device, dtype = detect_device()

model_id = "vikhyatk/moondream2"
tokenizer = AutoTokenizer.from_pretrained(model_id, revision=LATEST_REVISION)
moondream = Moondream.from_pretrained(
    model_id,
    revision=LATEST_REVISION,
    torch_dtype=dtype,
    ignore_mismatched_sizes=True
).to(device=device)
moondream.eval()

def query_ai(image_path, prompt="What is this?"):
    image = Image.open(image_path)
    image_embeds = moondream.encode_image(image)
    answer = moondream.answer_question(image_embeds, prompt, tokenizer)

    return answer

