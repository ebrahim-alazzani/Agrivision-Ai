import os
import shutil
import subprocess
from pathlib import Path

def download_and_deploy():
    kernel_id = "ebrahimalazzani/agrivision-ai-crop-disease-detection"
    temp_dir = Path("E:/New folder (3)/agrivision-ai/kaggle_kernel/outputs")
    mobile_assets_dir = Path("E:/New folder (3)/agrivision-ai/apps/farmer_mobile/assets/models")
    server_models_dir = Path("E:/New folder (3)/agrivision-ai/ai/registry/models")

    temp_dir.mkdir(parents=True, exist_ok=True)
    mobile_assets_dir.mkdir(parents=True, exist_ok=True)
    server_models_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Checking status of {kernel_id}...")
    status_cmd = f"python -m kaggle kernels status {kernel_id}"
    subprocess.run(status_cmd, shell=True)

    print(f"[*] Downloading outputs to {temp_dir}...")
    dl_cmd = f"python -m kaggle kernels output {kernel_id} -p \"{temp_dir}\""
    res = subprocess.run(dl_cmd, shell=True)

    if res.returncode == 0:
        print("[+] Outputs downloaded successfully!")
        # Copy to mobile assets
        onnx_file = temp_dir / "agrivision_plant_model.onnx"
        json_file = temp_dir / "class_indices.json"
        pth_file = temp_dir / "agrivision_plant_vision_best.pth"

        if onnx_file.exists():
            shutil.copy2(onnx_file, mobile_assets_dir / "agrivision_plant_model.onnx")
            print(f"[+] Copied ONNX model to {mobile_assets_dir / 'agrivision_plant_model.onnx'}")
        
        if json_file.exists():
            shutil.copy2(json_file, mobile_assets_dir / "class_indices.json")
            print(f"[+] Copied class_indices.json to {mobile_assets_dir / 'class_indices.json'}")

        if pth_file.exists():
            shutil.copy2(pth_file, server_models_dir / "agrivision_plant_vision_best.pth")
            print(f"[+] Copied PyTorch weights to {server_models_dir / 'agrivision_plant_vision_best.pth'}")

        print("[+] Artifacts deployment complete!")
    else:
        print("[-] Downloading outputs failed. The kernel might still be running.")

if __name__ == "__main__":
    download_and_deploy()
