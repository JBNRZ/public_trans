from random import randint, choices, choice, shuffle
from string import ascii_lowercase
from datetime import datetime
from faker import Faker

phone_prefix = [
    734, 735, 736, 737, 738, 739, 747, 748, 750, 751, 752, 757, 758, 759, 772, 778,
    782, 783, 784, 787, 788, 795, 798, 730, 731, 732, 740, 745, 746, 755, 756, 766,
    767, 771, 775, 776, 785, 786, 796, 733, 749, 753, 773, 774, 777, 780, 781, 789,
    790, 791, 793, 799
]
fake = Faker(locale='zh_CN')


def correct_data() -> tuple[str, str, str, str, str]:
    ssn = fake.ssn()
    return fake.name(), str(datetime.now().year - int(ssn[6:10])), str(choice(phone_prefix)) + fake.phone_number()[3:], ssn, fake.ipv4()


def reformat_ssn(ssn: str) -> str:
    if randint(0, 1) == 1:
        return f"{ssn[:6]}-{ssn[6:14]}-{ssn[14:]}"
    else:
        return f"{ssn[:6]} {ssn[6:14]} {ssn[14:]}"


def reformat_phone(phone: str) -> str:
    if randint(0, 1) == 1:
        return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
    else:
        return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"


def wrong_name() -> str:
    name = list(fake.name())
    name.insert(randint(1, len(name) - 1), "".join(choices(ascii_lowercase, k=randint(1, 3))))
    name = "".join(name)
    return name


def wrong_phone() -> str:
    prefix = 0
    while prefix == 0:
        tmp = randint(700, 800)
        if tmp not in phone_prefix:
            prefix = tmp
    return str(prefix) + fake.phone_number()[3:]


def wrong_ssn() -> str:
    ssn = list(fake.ssn())
    ssn[randint(0, len(ssn) - 1)] = str(randint(0, 9))
    return "".join(ssn)


def wrong_age(ssn: str) -> str:
    if not ssn[6:10].isdigit():
        return str(randint(20, 65))
    return str(datetime.now().year - int(ssn[6:10]) + randint(1, 15))


def wrong_ipv4() -> str:
    ipv4 = fake.ipv4().split(".")
    ipv4[randint(0, len(ipv4) - 1)] = str(randint(256, 500))
    return ".".join(ipv4)


def main():
    data = []

    for _ in range(1000):
        correct = list(correct_data())
        if randint(0, 1) == 1:
            correct[2] = reformat_phone(correct[2])
        if randint(0, 1) == 1:
            correct[3] = reformat_ssn(correct[3])
        data.append(correct)

    for _ in range(randint(400, 800)):
        correct = list(correct_data())
        wrong = wrong_name(), wrong_age(correct[3]), wrong_phone(), wrong_ssn(), wrong_ipv4()
        index = randint(0, len(correct) - 1)
        correct[index] = wrong[index]
        data.append(correct)

    shuffle(data)

    with open("data.csv", "w", encoding="utf-8") as f:
        f.write("id,name,age,phone,ssn,ip\n")
        for i in range(len(data)):
            f.write(f"{i + 1},{data[i][0]},{data[i][1]},{data[i][2]},{data[i][3]},{data[i][4]}\n")


if __name__ == "__main__":
    main()
