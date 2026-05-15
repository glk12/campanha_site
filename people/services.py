import re


def digits_only(value):
    return re.sub(r"\D", "", value or "")


def is_valid_cpf(cpf):
    cpf = digits_only(cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    for size in (9, 10):
        total = sum(int(cpf[index]) * ((size + 1) - index) for index in range(size))
        digit = ((total * 10) % 11) % 10
        if digit != int(cpf[size]):
            return False

    return True


def simulate_electoral_validation(cpf, fallback_city):
    cpf = digits_only(cpf)
    digits_sum = sum(int(digit) for digit in cpf)
    zone_number = int(cpf[2:5]) % 120 + 1
    section_number = int(cpf[5:8]) % 450 + 1
    status = "apto" if digits_sum % 3 != 0 else "not_apto"

    return {
        "voter_status": status,
        "electoral_zone": f"{zone_number:03d}",
        "electoral_section": f"{section_number:03d}",
        "voting_city": fallback_city or "Municipio nao informado",
        "validation_source": "simulated",
    }
