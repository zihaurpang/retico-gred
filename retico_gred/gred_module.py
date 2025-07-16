import os, sys
os.environ['CORE'] = 'retico-core'
sys.path.append(os.environ['CORE'])

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import retico_core
from retico_core import abstract, UpdateMessage, UpdateType
from retico_chatgpt.chatgpt import GPTTextIU
from retico_core.text import TextIU

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name = "bsu-slim/gred-misty"
model = AutoModelForCausalLM.from_pretrained(model_name).to(device).eval()
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)

class GREDTextIU(TextIU):
    @staticmethod
    def type():
        return TextIU.type()
    def __repr__(self):
        # show the full payload without truncation
        return f"{self.type()} - ({self.creator.name()}): {self.get_text()}"


class GREDActionGenerator(abstract.AbstractModule):
    @staticmethod
    def name():
        return "GRED Action Generator"
    @staticmethod
    def description():
        return "Generate robot‐behavior sequences from emotion labels."
    @staticmethod
    def input_ius():
        return [GPTTextIU]
    @staticmethod
    def output_iu():
        return GREDTextIU

    def __init__(self, model, tokenizer, device, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.current_text = ""

    def predict(self, emotion_label: str) -> str:
        prompt = f"<|startoftext|>Emotion: {emotion_label} <|endoftext|> Behaviors:"
        inputs = tokenizer(prompt, return_tensors="pt").to(device)

        # Generate behaviors
        output = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id
        )

        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
        return generated_text.split("Behaviors:")[1].strip()
    
    def process_update(self, update_message): 
                            # ignore incoming None
        recieved_update = False
        for iu, update_type in update_message:
            if update_type != UpdateType.COMMIT:
                continue
            if not isinstance(iu, GPTTextIU):
                continue
            
            recieved_update = True
            # extract the emotion label from the IU payload
            self.current_text = iu.payload.strip()
        
        if recieved_update:
            print(f"Received emotion label: {self.current_text}")
            
            # run the model once per iteration
            behavior = self.predict(self.current_text)
            print(f"Generated behavior for {self.current_text}: {behavior}")
            payload = f"{behavior}"
            # prepare result update
            output_iu = self.create_iu(None)
            output_iu.payload = payload
            output_iu = retico_core.UpdateMessage.from_iu(output_iu, retico_core.UpdateType.ADD)
            # print(f"GRED prediction result: {output_iu}")
            return output_iu
