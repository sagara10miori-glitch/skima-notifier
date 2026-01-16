import subprocess
import pkg_resources

def update_requirements():
    # pip を最新に
    subprocess.run(["pip", "install", "--upgrade", "pip"], check=True)

    # すべてのパッケージを最新に更新
    for dist in pkg_resources.working_set:
        subprocess.run(["pip", "install", "--upgrade", dist.project_name], check=False)

    # 最新バージョンを requirements.txt に書き出し
    with open("requirements.txt", "w") as f:
        for dist in pkg_resources.working_set:
            f.write(f"{dist.project_name}=={dist.version}\n")

    print("requirements.txt を最新化しました。")

if __name__ == "__main__":
    update_requirements()
