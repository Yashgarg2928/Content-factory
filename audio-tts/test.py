import os
import re
import sys
from importlib.resources import files
import soundfile as sf
import torch
import torchaudio
from omegaconf import OmegaConf
import argparse

sys.path.append(os.getcwd())  # add current directory to python path

from f5_tts.api import F5TTS
from f5_tts.model.utils import seed_everything

def process_reels(base_folder): #makes a list of paths of reel folders
    reel_paths = []
    for reel_folder in os.listdir(base_folder): #get path of each folder one by one
        if reel_folder.isdigit():  #checks if its a folder of reel or not 
            reel_paths.append(os.path.join(base_folder, reel_folder))
    return reel_paths


def batch_tts_multi_speaker(
    input_file,
    output_file="generated_audio/combined_output.wav",
    sample_rate=24000,  # You might need to adjust based on your actual model configuration
    device="cuda" if torch.cuda.is_available() else "cpu",  # Default to CUDA if available, else CPU
    debugging=True,  # Enable debugging mode
    **kwargs,
):
    """
    Performs batch TTS on a text file with inline speaker tags, creating a single combined audio file.

    Args:
        input_file (str): Path to the text file containing sentences with speaker tags.
        model_name (str): Name of the F5-TTS model to use.
        output_file (str): Path to save the combined audio file.
        sample_rate (int): sample rate of the output audio
        device (str): Device to run the model on ("cuda" or "cpu"). Defaults to CUDA if available.
        debugging (bool): Enable or disable debugging mode.
        **kwargs: Additional keyword arguments to pass to the F5TTS.infer() function.
    """

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file), exist_ok=True)


    with open(input_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f]

    all_audio_chunks = []  # Store audio chunks as PyTorch tensors on the specified device

    for line in lines:
        # Split each line into speaker tag and sentence
        match = re.match(r"\{([A-Za-z]+)\}\s\"(.*?)\"", line)
        if match:
            speaker_tag, gen_text = match.groups()
            gen_text = gen_text.strip()
        else:
            print(f"Skipping invalid line format: {line}")
            continue

        # Construct the reference audio path from the speaker tag
        ref_audio = f"{speaker_tag}.wav"

        # Check if the reference audio file exists
        if not os.path.exists(ref_audio):
            print(f"Error: Reference audio file not found for speaker '{speaker_tag}': {ref_audio}")
            continue

        print(f"Generating speech for {speaker_tag}: {gen_text}")

        try:
            # Debug:
            print(f"Before F5TTS.infer():")
            print(f"  ref_audio: {ref_audio}")
            # Print the content of the input audio
            # print(f"  Ref audio content: {torchaudio.load(ref_audio)[0].shape}")
            print(f"  gen_text: {gen_text}")

            wav, sr, _ = f5_tts.infer(
                ref_file=ref_audio,
                ref_text="",  # Let ASR do its job
                gen_text=gen_text,
                file_wave=None,  # Don't save intermediate files
                **kwargs,
            )

            # Debug:
            if debugging:
                print(f"After F5TTS.infer():")
                print(f"  Generated audio chunk (wav) shape: {wav.shape if isinstance(wav, torch.Tensor) else 'Not a Tensor'}")

            # Ensure generated audio is a PyTorch tensor on the specified device
            if not isinstance(wav, torch.Tensor):
                wav = torch.tensor(wav, dtype=torch.float32, device=device)
            elif wav.device != device:  # If the tensor is on the wrong device, move it.
                wav = wav.to(device)

            all_audio_chunks.append(wav)

        except Exception as e:
            print(f"Error generating speech for {speaker_tag}: {gen_text} - {e}")
            print(e)  # Print the full error

    # Concatenate all audio chunks
    if all_audio_chunks:
        concatenated_audio = torch.cat(all_audio_chunks)

        # Ensure concatenated audio is on the CPU before saving
        sf.write(output_file, concatenated_audio.cpu().numpy(), sample_rate)

        print(f"Saved combined audio to {output_file}")
    else:
        print("No audio generated. Check your input file and reference audio paths.")


if __name__ == "__main__":
    
    

    parser = argparse.ArgumentParser(description="Run batch TTS processing.")
    parser.add_argument("--base_folder", required=True, help="Path to base folder containing reel folders.")
    args = parser.parse_args()

    base_folder = args.base_folder

    reel_folders = process_reels(base_folder)
    
    # Optional arguments - adjust if you'd like
    model_name = "F5TTS_v1_Base"
    sway_sampling_coef = -1
    cfg_strength = 2
    nfe_step = 32
    speed = 1.0
    use_cuda = torch.cuda.is_available()  # Check CUDA availability
    device="cuda" if use_cuda else "cpu"

    f5_tts = F5TTS(model=model_name, device=device)  # Load model and vocoder only once
    print(f"Model loading done: {model_name}")

    for folder in reel_folders:

        input_file = os.path.join(folder,"audio.txt")  # Change to your input text file
        output_file = os.path.join(folder, "audio.wav")
        # the output_dir is now predefined and set to "generated_audio"
        # removed explicit speaker_audio_map

        batch_tts_multi_speaker(
            input_file=input_file,
            output_file=output_file,
            
            sway_sampling_coef=sway_sampling_coef,
            cfg_strength=cfg_strength,
            nfe_step=nfe_step,
            speed=speed,
            debugging=True,  # Enable debugging mode
            # Add any other F5TTS.infer() arguments here
        )