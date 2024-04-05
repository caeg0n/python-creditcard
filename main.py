import json
import re  # Import the regex module for input validation
from datetime import datetime
from operator import itemgetter
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_invoices_sorted_by_date(cards_file):
    cards = load_data(cards_file)
    all_invoices = []
    cards_with_invoices = set()
    for card, info in cards.items():
        for invoice in info['invoices']:
            invoice_date = datetime.strptime(invoice['date'], "%m/%y")
            all_invoices.append({'card': card, 'date': invoice_date, 'value': invoice['value']})
            cards_with_invoices.add(card)  # Add card to the set of cards that have invoices
    sorted_invoices = sorted(all_invoices, key=lambda x: x['value'], reverse=True)    
    green_start = "\033[92m"
    blue_start = "\033[94m"
    red_start = "\033[91m"
    color_reset = "\033[0m"    
    current_month_year = ""
    monthly_total = 0.0
    print(f"{green_start}Faturas Ordenadas por Valor (Maior Primeiro):{color_reset}")
    for invoice in sorted_invoices:
        invoice_month_year = invoice['date'].strftime('%Y-%m')
        if invoice_month_year != current_month_year:
            if current_month_year:
                formatted_total = f"{monthly_total:.2f}"
                print(f"{blue_start}Total de {current_month_year}: {formatted_total}{color_reset}")
            current_month_year = invoice_month_year
            monthly_total = 0.0
            print(f"\n{green_start}{current_month_year}:{color_reset}")
        monthly_total += invoice['value']
        formatted_value = f"{invoice['value']:.2f}"
        print(f"{green_start}Cartão: {invoice['card']}, Valor: {formatted_value}{color_reset}")    
    if current_month_year:
        formatted_total = f"{monthly_total:.2f}"
        print(f"{blue_start}Total de {current_month_year}: {formatted_total}{color_reset}")
    all_cards_set = set(cards.keys())
    missing_invoices_cards = all_cards_set - cards_with_invoices
    if missing_invoices_cards:
        print(f"\n{red_start}Cartões sem faturas informadas neste período:{color_reset}")
        for card in sorted(missing_invoices_cards):
            print(f"{red_start}{card}{color_reset}")

def list_invoices_for_month(cards_file):
    month_year = input("Digite o mês e ano para listar as faturas (mm/aa): ")
    if not re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", month_year):
        print("\033[91mFormato de data inválido. Por favor, use o formato mm/aa.\033[0m")
        return
    cards = load_data(cards_file)
    green_start = "\033[92m"
    color_reset = "\033[0m"
    print(f"{green_start}Faturas para {month_year}:{color_reset}")
    found = False
    for name, info in cards.items():
        for invoice in info['invoices']:
            if invoice['date'] == month_year:
                print(f"{green_start}Cartão de Crédito: {name}, Valor da Fatura: {invoice['value']}{color_reset}")
                found = True
    if not found:
        print(f"{green_start}Nenhuma fatura encontrada para {month_year}.{color_reset}")

def load_data(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}  # Return an empty dict if the file does not exist
    except json.JSONDecodeError:
        return {}

def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def register_credit_card(cards_file):
    name = input("Digite o nome do cartão de crédito: ")
    credit_limit = input("Digite o limite de crédito: ")
    cards = load_data(cards_file)
    cards[name] = {'credit_limit': float(credit_limit), 'invoices': []}
    save_data(cards_file, cards)
    print(f"{name} foi registrado(a) com sucesso!")

def show_credit_cards_sorted(cards_file):
    cards = load_data(cards_file)
    # Ordena os cartões por limite de crédito em ordem decrescente
    sorted_cards = sorted(cards.items(), key=lambda x: x[1]['credit_limit'], reverse=True)
    green_start = "\033[92m"  # Inicia a cor verde para a listagem
    light_blue_start = "\033[96m"  # Inicia a cor azul claro para o total
    color_reset = "\033[0m"  # Reseta para a cor padrão
    total_limit = 0  # Inicializa a soma dos limites
    for name, info in sorted_cards:
        print(f"{green_start}Nome: {name}, Limite de Crédito: {info['credit_limit']}{color_reset}")
        total_limit += info['credit_limit']  # Adiciona o limite de crédito atual ao total    
    # Após listar os cartões, exibe o total dos limites em azul claro
    print(f"{light_blue_start}Total dos Limites dos Cartões de Crédito: {total_limit}{color_reset}")


def list_credit_cards_with_id(cards_file):
    cards = load_data(cards_file)
    sorted_cards = sorted(cards.items(), key=lambda x: x[0])
    if not sorted_cards:
        print("Nenhum cartão de crédito registrado ainda.")
        return None
    print("\nCartões de Crédito Registrados:")
    for idx, (name, info) in enumerate(sorted_cards, start=1):
        print(f"{idx}. {name} - Limite de Crédito: {info['credit_limit']}")
    return sorted_cards

def register_invoice(cards_file):
    sorted_cards = list_credit_cards_with_id(cards_file)
    if sorted_cards is None:
        return    
    try:
        selection = int(input("Selecione um cartão de crédito pelo ID: ")) - 1
        if selection < 0 or selection >= len(sorted_cards):
            raise ValueError("ID inválido selecionado.")
        selected_card_name = sorted_cards[selection][0]
        date_input = input("Digite o mês e ano (mm/aa): ")
        if not re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", date_input):
            raise ValueError("Formato de data inválido. Por favor, use o formato mm/aa.")
        cards = load_data(cards_file)
        if any(invoice['date'] == date_input for invoice in cards[selected_card_name]['invoices']):
            raise ValueError("Uma fatura para este mês já existe.")
        value = float(input("Digite o valor da fatura: "))
        cards[selected_card_name]['invoices'].append({'date': date_input, 'value': value})
        save_data(cards_file, cards)
        print(f"Fatura registrada com sucesso para {selected_card_name}.")
    except ValueError as e:
        red_start = "\033[91m"
        color_reset = "\033[0m"
        print(f"{red_start}{e}{color_reset}")

def payment_strategy(cards_file):
    month_year = input("Digite o mês e ano da fatura no formato mm/aa: ")
    cards = load_data(cards_file)
    if not cards:
        print("\033[91mNão foram encontradas faturas para este período.\033[0m")
        return
    total_paid = 0
    for card, info in cards.items():
        for invoice in info['invoices']:
            if invoice['date'] == month_year and 'paid' in invoice:
                total_paid += invoice['paid']
    try:
        user_input = input(f"Digite o valor máximo total para pagamento [Padrão: {total_paid:.2f}]: ").strip()
        available_payment = float(user_input) if user_input else total_paid
    except ValueError:
        print("\033[91mValor inválido.\033[0m")
        return
    invoices = [
        {'card': card, 'value': invoice['value'], 'paid': 0, 'min_payment': invoice['value'] * 0.15, 'date': invoice['date']}
        for card, info in cards.items()
        for invoice in info['invoices'] if invoice['date'] == month_year
    ]
    total_min_payment = sum(inv['min_payment'] for inv in invoices)
    if available_payment < total_min_payment:
        for inv in invoices:
            inv['paid'] = (available_payment / total_min_payment) * inv['min_payment']
    else:
        for inv in invoices:
            inv['paid'] = inv['min_payment']
            available_payment -= inv['min_payment']
        if available_payment > 0:
            extra_payment_distribution(invoices, available_payment)
    for inv in invoices:
        for card_info in cards[inv['card']]['invoices']:
            if card_info['date'] == inv['date']:
                card_info['paid'] = inv['paid']    
    save_data(cards_file, cards)
    display_results(invoices)

def extra_payment_distribution(invoices, available_payment):
    invoices.sort(key=lambda inv: inv['value'] - inv['paid'])
    for inv in invoices:
        remaining_due = inv['value'] - inv['paid']
        if available_payment <= 0:
            break
        payment = min(remaining_due, available_payment)
        inv['paid'] += payment
        available_payment -= payment

def display_results(invoices):
    total_interest = 0
    total_remaining_due = 0 
    for inv in invoices:
        remaining_due = inv['value'] - inv['paid']
        interest = remaining_due * 0.14
        total_interest += interest
        total_remaining_due += remaining_due
        if remaining_due <= 0.01:
            color_start = "\033[92m" 
        else:
            color_start = "\033[91m"
        print(f"{color_start}Cartão: {inv['card']}, Valor: {inv['value']:.2f}, Pago: {inv['paid']:.2f}, Restante: {remaining_due:.2f}, Juros: {interest:.2f}\033[0m")
    print(f"\033[0mTotal de Juros: {total_interest:.2f}")
    print(f"Total Restante Devido de Todas as Faturas: {total_remaining_due:.2f}")  # Print total remaining due
    
def show_saved_states_by_year(cards_file):
    selected_year = input("Digite o ano para visualizar as faturas salvas (aaaa): ")
    cards = load_data(cards_file)
    found_invoices = False
    for card, details in cards.items():
        for invoice in details['invoices']:
            if invoice['date'].endswith(selected_year):
                print(f"Cartão: {card}, Data: {invoice['date']}, Valor: {invoice['value']}")
                found_invoices = True
    if not found_invoices:
        print("Nenhuma fatura encontrada para o ano selecionado.")

def installment_payment_strategy(cards_file):
    month_year = input("Digite o mês e ano da fatura no formato mm/aa: ")
    try:
        total_payment = float(input("Digite o valor total disponível para pagamento: "))
    except ValueError:
        print("\033[91mValor inválido.\033[0m")
        return    
    cards = load_data(cards_file)
    invoices = [
        {'card': card, 'date': invoice['date'], 'value': invoice['value'], 'paid': 0, 'interest_due': 0, 'division_factor': 1, 'division_value': invoice['value']}  # Include 'division_value'
        for card, info in cards.items()
        for invoice in info['invoices'] if invoice['date'] == month_year
    ]
    invoices, remaining_funds = ensure_minimum_payments(invoices, total_payment)
    updated_invoices, remaining_funds = allocate_remaining_payments(invoices, remaining_funds)
    for inv in updated_invoices:
        if inv['value'] > 0 and inv['paid'] > 0:
            inv['division_factor'] = round(inv['value'] / inv['paid'])
            inv['division_value'] = inv['value'] / inv['division_factor']
    RED = "\033[91m"
    GREEN = "\033[92m"
    RESET = "\033[0m"    
    for inv in updated_invoices:
        paid_rounded = round(inv['paid'], 2)
        remaining_due = round(inv['value'] - inv['paid'], 2)
        interest_due_rounded = round(inv['interest_due'], 2)
        division_value_rounded = round(inv['division_value'], 2)
        color = GREEN if remaining_due == 0 else RED
        print(f"{color}Cartão: {inv['card']}, Fatura: {inv['value']:.2f}, Pago: {paid_rounded:.2f}, Restante: {remaining_due:.2f}, Juros: {interest_due_rounded:.2f}, Fator de Divisão: {inv['division_factor']}, Valor por Divisão: {division_value_rounded:.2f}{RESET}")    
    if remaining_funds > 0:
        print(f"Fundos não utilizados: {round(remaining_funds, 2):.2f}")

def allocate_remaining_payments(invoices, available_funds):
    invoices.sort(key=lambda inv: inv['value'] - inv['paid'])
    for inv in invoices:
        if available_funds <= 0:
            inv['interest_due'] = (inv['value'] - inv['paid']) * 0.14
            continue  # Move to the next invoice        
        remaining_due = inv['value'] - inv['paid']
        payable_amount = min(remaining_due, available_funds)
        inv['paid'] += payable_amount
        available_funds -= payable_amount
        remaining_due_after_payment = inv['value'] - inv['paid']
        if remaining_due_after_payment > 0:
            inv['interest_due'] = remaining_due_after_payment * 0.14
        else:
            inv['interest_due'] = 0
    return invoices, available_funds

def ensure_minimum_payments(invoices, available_funds):
    for inv in invoices:
        min_payment_required = inv['value'] * 0.15
        if inv['paid'] < min_payment_required:
            additional_payment_needed = min_payment_required - inv['paid']
            if available_funds >= additional_payment_needed:
                inv['paid'] += additional_payment_needed
                available_funds -= additional_payment_needed
            else:
                for inv in invoices:
                    proportion = additional_payment_needed / sum(inv['value'] * 0.15 for inv in invoices)
                    payment = available_funds * proportion
                    inv['paid'] += payment
                    available_funds -= payment
                break
    return invoices, available_funds
   
def allocate_payments(invoices, available_funds):
    invoices.sort(key=lambda inv: inv['value'])
    for inv in invoices:
        if available_funds == 0:
            break  # Stop if we run out of funds
        payable_amount = min(inv['value'], available_funds)
        inv['paid'] += payable_amount
        available_funds -= payable_amount
        remaining_due = inv['value'] - inv['paid']
        if remaining_due > 0:
            inv['interest_due'] = remaining_due * 0.14
        else:
            inv['interest_due'] = 0
    return invoices, available_funds


def main():
    CARDS_FILE = 'credit_cards.json'
    while True:
        red = "\033[91m"
        green = "\033[92m"
        yellow = "\033[93m"
        blue = "\033[94m"
        magenta = "\033[95m"
        cyan = "\033[96m"
        color_reset = "\033[0m"
        print("\nMenu:")
        print(f"{red}1. Registrar um novo cartão de crédito{color_reset}")
        print(f"{green}2. Mostrar cartões de crédito ordenados por limite{color_reset}")
        print(f"{yellow}3. Registrar uma fatura para um cartão de crédito{color_reset}")
        print(f"{blue}4. Listar todas as faturas de um mês específico{color_reset}")
        print(f"{magenta}5. Mostrar todas as faturas ordenadas por mês/ano{color_reset}")
        print(f"{yellow}6. Opções de pagamento{color_reset}")
        print(f"{blue}7. Visualizar faturas salvas por ano{color_reset}")
        print(f"{cyan}8. Pagamento Parcelado{color_reset}")
        print(f"{magenta}9. Sair{color_reset}")
        choice = input("Digite sua escolha: ")
        if choice == '1':
            register_credit_card(CARDS_FILE)
        elif choice == '2':
            show_credit_cards_sorted(CARDS_FILE)
        elif choice == '3':
            register_invoice(CARDS_FILE)
        elif choice == '4':
            list_invoices_for_month(CARDS_FILE)
        elif choice == '5':
            show_invoices_sorted_by_date(CARDS_FILE)
        elif choice == '6':
            payment_strategy(CARDS_FILE)
        elif choice == '7':
            show_saved_states_by_year(CARDS_FILE)
        elif choice == '8':
            installment_payment_strategy(CARDS_FILE)
        elif choice == '9':
            print(f"{cyan}Saindo...{color_reset}")
            break
        else:
            print(f"{red}Opção inválida. Por favor, tente novamente.{color_reset}")
        
        input("\nPressione ENTER para voltar ao menu principal...")
        clear_screen()

if __name__ == "__main__":
    main()