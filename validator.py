from re import compile
from datetime import datetime
from string import ascii_lowercase
from generator import phone_prefix


def validate_name(name: str) -> bool:
    return not any([True for i in name if i in ascii_lowercase])


def validate_age(age: str, ssn: str) -> bool:
    return int(age) == 2025 - int(ssn[6:10])


def validate_phone(phone: str) -> bool:
    return int(phone[:3]) in phone_prefix


def validate_ssn(ssn: str) -> bool:
    pattern = compile(r'^\d{17}[\dXx]$')
    if not pattern.match(ssn):
        return False

    birth_date_str = ssn[6:14]
    try:
        datetime.strptime(birth_date_str, "%Y%m%d")
    except ValueError:
        return False

    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

    sum_val = 0
    for i in range(17):
        sum_val += int(ssn[i]) * weights[i]

    idx = sum_val % 11
    if ssn[-1].upper() == check_codes[idx]:
        return True
    else:
        return False


def validate_ipv4(ipv4: str) -> bool:
    for i in ipv4.split("."):
        if int(i) < 0 or int(i) > 255:
            return False
    return True


def main():
    with open("data.csv", "r", encoding="utf-8") as f:
        data = f.read().strip().split("\n")[1:]

    with open("correct.csv", "w", encoding="utf-8") as f:
        f.write("id,name,age,phone,ssn,ip\n")
        for i in data:
            i = i.split(",")
            _id, name, age, phone, ssn, ip = i[0], i[1], i[2], i[3].replace("-", "").replace(" ", ""), i[4].replace("-", "").replace(" ", ""), i[5]
            if all([validate_name(name), validate_age(age, ssn), validate_phone(phone), validate_ssn(ssn), validate_ipv4(ip)]):
                f.write(f"{_id},{name},{age},{phone},{ssn},{ip}\n")


if __name__ == "__main__":
    main()
