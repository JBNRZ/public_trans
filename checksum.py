from hashlib import md5

def calc(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        data = f.read().strip().split("\n")[1:]
    data = [i.strip() for i in data]
    return md5("\n".join(data).encode()).hexdigest()


if __name__ == "__main__":
    print(calc("correct.csv"))
