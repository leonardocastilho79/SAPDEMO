#!/bin/bash
# Script de início rápido para o gerador de relatórios HANA

echo "=========================================="
echo "Gerador de Relatórios SAP HANA"
echo "Script de Início Rápido"
echo "=========================================="
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python 3 não está instalado."
    echo "Por favor, instale o Python 3.7 ou superior."
    exit 1
fi

echo "✓ Python encontrado: $(python3 --version)"
echo ""

# Verificar se as dependências estão instaladas
echo "Verificando dependências..."
if ! python3 -c "import hdbcli" 2>/dev/null; then
    echo "⚠ Dependências não instaladas. Instalando..."
    pip install -r requirements.txt
else
    echo "✓ Dependências OK"
fi
echo ""

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠ Arquivo .env não encontrado."
    echo "Copiando .env.example para .env..."
    cp .env.example .env
    echo ""
    echo "ATENÇÃO: Por favor, edite o arquivo .env com suas credenciais HANA"
    echo "Arquivo: $(pwd)/.env"
    echo ""
    read -p "Pressione ENTER depois de configurar o .env..."
fi

echo ""
echo "Iniciando geração de relatórios..."
echo ""

# Executar o programa
python3 main.py "$@"

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "=========================================="
    echo "✓ Relatórios gerados com sucesso!"
    echo "Verifique o diretório 'reports/'"
    echo "=========================================="
else
    echo "=========================================="
    echo "✗ Erro ao gerar relatórios"
    echo "Verifique o arquivo hana_reports.log"
    echo "=========================================="
fi

exit $exit_code
