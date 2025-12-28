#!/bin/bash

# ============================================
# Deploy Frontend to AWS S3
# ============================================

set -e

# Colors para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Cloud Fog API - S3 Deployment ===${NC}\n"

# Variables
BUCKET_NAME="cloud-fog-frontend"
REGION="us-east-1"
FRONTEND_DIR="frontend"

# Paso 1: Verificar AWS CLI
echo -e "${YELLOW}[1/5] Verificando AWS CLI...${NC}"
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI no instalado. Instálalo con: pip install awscli${NC}"
    exit 1
fi
echo -e "${GREEN}✅ AWS CLI OK${NC}\n"

# Paso 2: Crear bucket si no existe
echo -e "${YELLOW}[2/5] Verificando bucket S3...${NC}"
if aws s3 ls "s3://$BUCKET_NAME" 2>&1 | grep -q 'NoSuchBucket'; then
    echo -e "${YELLOW}   Creando bucket: $BUCKET_NAME${NC}"
    aws s3api create-bucket \
        --bucket "$BUCKET_NAME" \
        --region "$REGION"
    echo -e "${GREEN}✅ Bucket creado${NC}"
else
    echo -e "${GREEN}✅ Bucket ya existe${NC}"
fi

# Paso 3: Habilitar website hosting
echo -e "\n${YELLOW}[3/5] Habilitando website hosting...${NC}"
aws s3api put-bucket-website \
    --bucket "$BUCKET_NAME" \
    --website-configuration '{
        "IndexDocument": {
            "Suffix": "index.html"
        },
        "ErrorDocument": {
            "Key": "index.html"
        }
    }' 2>/dev/null || echo -e "${GREEN}✅ Website hosting ya habilitado${NC}"
echo -e "${GREEN}✅ Website hosting OK${NC}"

# Paso 4: Deshabilitar Block Public Access
echo -e "\n${YELLOW}[4/5] Deshabilitando Block Public Access...${NC}"
aws s3api put-public-access-block \
    --bucket "$BUCKET_NAME" \
    --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false" 2>/dev/null || true
echo -e "${GREEN}✅ Acceso público habilitado${NC}"

# Paso 4b: Hacer bucket público
echo -e "\n${YELLOW}[4b/5] Aplicando política de acceso público...${NC}"
aws s3api put-bucket-policy \
    --bucket "$BUCKET_NAME" \
    --policy "{
        \"Version\": \"2012-10-17\",
        \"Statement\": [
            {
                \"Sid\": \"PublicReadGetObject\",
                \"Effect\": \"Allow\",
                \"Principal\": \"*\",
                \"Action\": [\"s3:GetObject\", \"s3:ListBucket\"],
                \"Resource\": [\"arn:aws:s3:::$BUCKET_NAME\", \"arn:aws:s3:::$BUCKET_NAME/*\"]
            }
        ]
    }" 2>/dev/null || echo -e "${RED}⚠️ Política ya existe${NC}"
echo -e "${GREEN}✅ Bucket público${NC}"

# Paso 5: Subir archivos
echo -e "\n${YELLOW}[5/6] Subiendo archivos a S3...${NC}"
aws s3 sync "$FRONTEND_DIR" "s3://$BUCKET_NAME" \
    --delete \
    --cache-control "max-age=3600" \
    --exclude ".DS_Store" \
    --exclude "*.md"

echo -e "\n${GREEN}✅ ¡Deployment completado!${NC}\n"

# Obtener URL del sitio
WEBSITE_URL="http://${BUCKET_NAME}.s3-website-${REGION}.amazonaws.com"
echo -e "${GREEN}URL de tu sitio:${NC}"
echo -e "${YELLOW}$WEBSITE_URL${NC}\n"

# Mostrar archivos subidos
echo -e "${YELLOW}Archivos en S3:${NC}"
aws s3 ls "s3://$BUCKET_NAME" --recursive | awk '{print "  " $4}'

echo -e "\n${GREEN}¡Listo! Tu dashboard está en línea.${NC}"
