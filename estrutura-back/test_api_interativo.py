"""
Script interativo para testar a API e visualizar dados em tempo real.
Permite criar dados de teste, fazer queries e ver tudo que está no banco.
"""

import requests
import json
from datetime import datetime
import sys

BASE_URL = "http://localhost:8000"

# Cores para terminal
VERDE = '\033[92m'
AZUL = '\033[94m'
AMARELO = '\033[93m'
VERMELHO = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'
CYAN = '\033[96m'

def print_sucesso(msg):
    print(f"{VERDE}✅ {msg}{RESET}")

def print_info(msg):
    print(f"{AZUL}ℹ️  {msg}{RESET}")

def print_alerta(msg):
    print(f"{AMARELO}⚠️  {msg}{RESET}")

def print_erro(msg):
    print(f"{VERMELHO}❌ {msg}{RESET}")

def print_titulo(msg):
    print(f"\n{BOLD}{CYAN}{'='*70}{RESET}")
    print(f"{BOLD}{CYAN}{msg.center(70)}{RESET}")
    print(f"{BOLD}{CYAN}{'='*70}{RESET}\n")

def print_subtitulo(msg):
    print(f"\n{BOLD}{AZUL}▶ {msg}{RESET}")
    print(f"{AZUL}{'─'*50}{RESET}\n")

# ============================================================================
# MAIN MENU
# ============================================================================

def menu_principal():
    """Exibe menu principal"""
    print_titulo("🧪 TESTE INTERATIVO DE API")
    
    print(f"""
{BOLD}Opções disponíveis:{RESET}

  1. 📊 Ver status do banco
  2. 👥 Listar usuários
  3. 📍 Listar locais
  4. 📈 Listar registros
  5. 🔍 Buscar registros por local
  6. 💾 Popular banco com dados de teste
  7. 🗑️  Limpar banco (CUIDADO!)
  8. 🚀 Rodar seed_dados_teste.py
  0. ❌ Sair
    """)

def exibir_status():
    """Exibe status do banco de dados"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_subtitulo("Status do Banco de Dados")
            
            info = [
                ["👥 Usuários cadastrados", data.get('usuarios_cadastrados', 0)],
                ["📍 Locais cadastrados", data.get('locais_cadastrados', 0)],
                ["📊 Registros totais", data.get('registros_totais', 0)],
                ["🕐 Timestamp", data.get('timestamp', 'N/A')],
                ["✅ Status", data.get('status', 'N/A')]
            ]
            
            # Simples formatação de tabela
            print(f"{BOLD}{'─'*50}{RESET}")
            for row in info:
                print(f"  {row[0]:<30} {VERDE}{row[1]}{RESET}")
            print(f"{BOLD}{'─'*50}{RESET}")
            return True
        else:
            print_erro("Erro ao obter status")
            return False
    except Exception as e:
        print_erro(f"Erro de conexão: {str(e)}")
        return False

def listar_usuarios():
    """Lista todos os usuários"""
    print_subtitulo("Usuários Cadastrados")
    try:
        # Na API atual, não temos endpoint para listar usuários
        # Mas podemos simular a resposta baseado no conhecimento do código
        print_alerta("Nota: Listagem de usuários não disponível via API")
        print_info("Use a aba 'Perfil' no frontend para ver dados do usuário logado")
        return
    except Exception as e:
        print_erro(f"Erro: {str(e)}")

def listar_locais():
    """Lista todos os locais"""
    print_subtitulo("Locais Cadastrados")
    try:
        # Tenta via endpoint de busca
        response = requests.get(
            f"{BASE_URL}/tipos-ambiente",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print_info(f"Total de tipos de ambiente: {len(data)}")
                for tipo in data:
                    print(f"  • {tipo}")
            else:
                print_info("Tipos de ambiente disponíveis:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print_alerta("Endpoint de locais não disponível")
    except Exception as e:
        print_erro(f"Erro: {str(e)}")

def listar_registros():
    """Lista informações sobre registros"""
    print_subtitulo("Informações sobre Registros")
    print_alerta("Nota: Detalhes completos apenas com autenticação")
    print_info("Para visualizar registros, faça login e vá para 'Buscar Locais'")
    print_info("Os registros são salvos com:\n")
    
    registro_exemplo = {
        "id": "UUID",
        "place_id": "local_unico",
        "usuario_email": "usuario@email.com",
        "timestamp": "2025-10-20T20:30:00",
        "ruido_db": 52.3,
        "luminosidade_lux": 450.5,
        "nivel_ruido": "Ok",
        "nivel_luz": "Ok"
    }
    
    for chave, valor in registro_exemplo.items():
        print(f"  • {BOLD}{chave}{RESET}: {valor}")

def buscar_por_local():
    """Busca registros por local"""
    print_subtitulo("Buscar Registros por Local")
    local_name = input(f"{AZUL}📍 Digite o nome do local (ex: 'Starbucks'): {RESET}")
    
    if not local_name:
        print_alerta("Nome do local não pode estar vazio")
        return
    
    try:
        # Simula busca (na API real seria via endpoint dedicado)
        print_info(f"Buscando registros para '{local_name}'...")
        print_alerta("Para buscar com precisão, use o frontend em 'Buscar Locais'")
    except Exception as e:
        print_erro(f"Erro: {str(e)}")

def popular_banco_manual():
    """Popula o banco com dados de teste manualmente"""
    print_subtitulo("Popular Banco Manualmente")
    
    print(f"""
{BOLD}Esta função criará:{RESET}
  • 3 usuários de teste
  • 7 locais em São Paulo
  • 10-15 registros de medições
  
{AMARELO}Isso pode levar alguns segundos...{RESET}
    """)
    
    confirmacao = input(f"{AZUL}Deseja continuar? (s/n): {RESET}").lower()
    if confirmacao != 's':
        print_alerta("Operação cancelada")
        return
    
    print_info("Iniciando população do banco...")
    print_info("Aguarde...")
    
    import subprocess
    try:
        resultado = subprocess.run(
            ["python3", "seed_dados_teste.py"],
            cwd="/Users/kimgomes/Desktop/sensorial_app/estrutura-back",
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(resultado.stdout)
        if resultado.stderr:
            print_alerta("Warnings/Erros:")
            print(resultado.stderr)
        
        if resultado.returncode == 0:
            print_sucesso("Banco populado com sucesso!")
        else:
            print_erro(f"Script retornou código: {resultado.returncode}")
            
    except subprocess.TimeoutExpired:
        print_erro("Script demorou muito tempo (timeout)")
    except Exception as e:
        print_erro(f"Erro ao executar script: {str(e)}")

def limpar_banco():
    """Limpa o banco de dados"""
    print_subtitulo("⚠️  OPERAÇÃO PERIGOSA: LIMPAR BANCO")
    
    print(f"""{VERMELHO}
    ⚠️  AVISO: Esta operação é IRREVERSÍVEL!
    ⚠️  Todos os dados serão perdidos!
    ⚠️  Digite 'CONFIRMAR' em MAIÚSCULA para prosseguir
    {RESET}
    """)
    
    confirmacao = input(f"{VERMELHO}Confirmação: {RESET}").strip()
    
    if confirmacao != "CONFIRMAR":
        print_alerta("Operação cancelada")
        return
    
    try:
        # Na API atual, não temos endpoint DELETE para limpar tudo
        # Precisaríamos reiniciar o servidor
        print_alerta("Para limpar o banco completamente:")
        print_info("  1. Interrompa o servidor (Ctrl+C)")
        print_info("  2. Reinicie: python3 main.py")
        print_info("  (Os dados são armazenados em memória, então reiniciar limpa tudo)")
    except Exception as e:
        print_erro(f"Erro: {str(e)}")

def testar_conexao():
    """Testa se a API está respondendo"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print_sucesso("✅ API respondendo em http://localhost:8000")
            return True
        else:
            print_erro("❌ API não respondendo corretamente")
            return False
    except:
        print_erro("❌ API não está respondendo!")
        print_alerta("Inicie o backend com: cd estrutura-back && python3 main.py")
        return False

# ============================================================================
# MAIN
# ============================================================================

def main():
    print_titulo("🧪 TESTE INTERATIVO DE API - SENSORIAL APP")
    
    # Testa conexão
    if not testar_conexao():
        print_alerta("Encerrando...")
        return
    
    print_sucesso("Conexão estabelecida!\n")
    
    while True:
        menu_principal()
        opcao = input(f"{AZUL}Escolha uma opção (0-8): {RESET}").strip()
        
        if opcao == "1":
            exibir_status()
        elif opcao == "2":
            listar_usuarios()
        elif opcao == "3":
            listar_locais()
        elif opcao == "4":
            listar_registros()
        elif opcao == "5":
            buscar_por_local()
        elif opcao == "6":
            popular_banco_manual()
        elif opcao == "7":
            limpar_banco()
        elif opcao == "8":
            print_info("Executando seed_dados_teste.py...")
            popular_banco_manual()
        elif opcao == "0":
            print(f"\n{VERDE}👋 Até logo!{RESET}\n")
            break
        else:
            print_erro("Opção inválida!")
        
        input(f"\n{AZUL}Pressione ENTER para continuar...{RESET}")
        print("\n" * 2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{AMARELO}⏸️  Programa interrompido{RESET}\n")
    except Exception as e:
        print_erro(f"Erro: {str(e)}")
