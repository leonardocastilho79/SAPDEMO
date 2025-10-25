#!/bin/bash
# Script de instalação do Gerador de Relatórios SAP HANA

echo "=========================================="
echo "Instalador - Gerador de Relatórios HANA"
echo "=========================================="
echo ""

# Verificar Python
echo "1. Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "   ✗ Python 3 não encontrado"
    echo "   Por favor, instale Python 3.7 ou superior"
    exit 1
fi
echo "   ✓ Python encontrado: $(python3 --version)"
echo ""

# Verificar pip
echo "2. Verificando pip..."
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "   ✗ pip não encontrado"
    echo "   Por favor, instale pip"
    exit 1
fi
echo "   ✓ pip encontrado"
echo ""

# Instalar dependências
echo "3. Instalando dependências Python..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "   ✓ Dependências instaladas com sucesso"
else
    echo "   ✗ Erro ao instalar dependências"
    exit 1
fi
echo ""

# Criar diretórios necessários
echo "4. Criando estrutura de diretórios..."
mkdir -p reports
mkdir -p config
echo "   ✓ Diretórios criados"
echo ""

# Configurar arquivo .env
echo "5. Configurando arquivo de ambiente..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   ✓ Arquivo .env criado"
    echo "   ⚠ IMPORTANTE: Edite o arquivo .env com suas credenciais HANA"
else
    echo "   ⚠ Arquivo .env já existe (não sobrescrito)"
fi
echo ""

# Tornar scripts executáveis
echo "6. Configurando permissões..."
chmod +x main.py
chmod +x quick_start.sh
echo "   ✓ Permissões configuradas"
echo ""

echo "=========================================="
echo "✓ Instalação concluída com sucesso!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "1. Edite o arquivo .env com suas credenciais:"
echo "   nano .env"
echo ""
echo "2. Execute o gerador de relatórios:"
echo "   ./quick_start.sh"
echo "   ou"
echo "   python3 main.py"
echo ""
echo "Para mais informações, consulte o README.md"
echo ""
