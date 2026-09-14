#!/usr/bin/env python3
"""
==============================================
📁 ORGANIZADOR DE PASTAS - GOOGLE DRIVE
==============================================
Cria automaticamente toda a estrutura de pastas
no Google Drive para organizar seus vídeos de vendas.

Dependências:
    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

Autor: Nandalin
==============================================
"""

import os
import sys
import json
from pathlib import Path

# ========================================
# TENTAR IMPORTAR DEPENDÊNCIAS
# ========================================
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import pickle
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

# ========================================
# CONFIGURAÇÃO DAS PASTAS
# ========================================

# Estrutura completa de pastas para o projeto
ESTRUTURA_PASTAS = {
    "📁 NANDALIN - Vídeos de Vendas": {
        "📂 01 - ROTEIROS E PLANEJAMENTO": {
            "📂 Roteiros Prontos": [],
            "📂 Roteiros em Produção": [],
            "📂 Roteiros Finalizados": [],
            "📂 Planejamento Semanal": [],
            "📂 Calendário de Postagens": [],
        },
        "📂 02 - VÍDEOS brutos (sem edição)": {
            "📂 Stories (9:16)": [],
            "📂 Completos (16:9)": [],
            "📂 Behind the Scenes": [],
            "📂 Depoimentos": [],
            "📂 Ensaio / Testes": [],
        },
        "📂 03 - VÍDEOS processados (após scripts)": {
            "📂 Stories - Finalizados": [],
            "📂 Completos - Finalizados": [],
            "📂 Reels - Otimizados": [],
            "📂 TikTok - Otimizados": [],
        },
        "📂 04 - THUMBNAILS E CAPAS": {
            "📂 Thumbnails YouTube": [],
            "📂 Thumbnails Instagram": [],
            "📂 Capas de E-book": [],
            "📂 Imagens de Produto": [],
            "📂 Arquivos Editáveis (PSD/Canva)": [],
        },
        "📂 05 - ÁUDIO E MÚSICAS": {
            "📂 Músicas Livres de Direitos": [],
            "📂 Efeitos Sonoros": [],
            "📂 Narração / Voz Off": [],
            "📂 Podcasts": [],
        },
        "📂 06 - MATERIAIS PARA LANÇAMENTO": {
            "📂 Vídeos de Pré-Lançamento": [],
            "📂 Vídeos de Lançamento": [],
            "📂 Vídeos de Escassez": [],
            "📂 Vídeos de Encerramento": [],
            "📂 Materiais para Anúncios": [],
        },
        "📂 07 - LINKS COMPARTILHADOS": {
            "📂 Links Google Drive (para clientes)": [],
            "📂 Links para Instagram Bio": [],
            "📂 Links para WhatsApp": [],
            "📂 Links para E-mail Marketing": [],
            "📂 Links para Anúncios Pagos": [],
        },
        "📂 08 - RESULTADOS E MÉTRICAS": {
            "📂 Prints de Métricas": [],
            "📂 Planilhas de Vendas": [],
            "📂 Relatórios Semanais": [],
            "📂 Relatórios Mensais": [],
            "📂 Prints de Depoimentos": [],
        },
        "📂 09 - MODELOS E TEMPLATES": {
            "📂 Templates de Vídeo": [],
            "📂 Templates de Thumbnail": [],
            "📂 Templates de E-mail": [],
            "📂 Templates de Mensagem WhatsApp": [],
            "📂 Templates de Post Instagram": [],
        },
        "📂 10 - ARQUIVO E HISTÓRICO": {
            "📂 Vídeos Antigos (backup)": [],
            "📂 Roteiros Antigos": [],
            "📂 Campanhas Anteriores": [],
        },
    }
}

# ========================================
# TEXTOS INFORMATIVOS PARA CADA PASTA
# ========================================

TEXTO_DESCRICAO = """
╔══════════════════════════════════════════════════════════╗
║  📁 ESTRUTURA DE PASTAS CRIADA COM SUCESSO!             ║
║                                                          ║
║  Sua organização no Google Drive está pronta para usar.  ║
╚══════════════════════════════════════════════════════════╝

📂 NANDALIN - Vídeos de Vendas
│
├── 📂 01 - ROTEIROS E PLANEJAMENTO
│   ├── Roteiros Prontos ........... Roteiros acabados
│   ├── Roteiros em Produção ....... Roteiros sendo escritos
│   ├── Roteiros Finalizados ....... Aprovados para gravação
│   ├── Planejamento Semanal ........ Metas da semana
│   └── Calendário de Postagens .... Programação mensal
│
├── 📂 02 - VÍDEOS brutos (sem edição)
│   ├── Stories (9:16) ............. Vídeos verticais brutos
│   ├── Completos (16:9) ........... Vídeos completos brutos
│   ├── Behind the Scenes .......... Bastidores
│   ├── Depoimentos ................ Clientes falando
│   └── Ensaio / Testes ............ Testes de câmera
│
├── 📂 03 - VÍDEOS processados (após scripts)
│   ├── Stories - Finalizados ...... Prontos para postar
│   ├── Completos - Finalizados .... Prontos para YouTube
│   ├── Reels - Otimizados ......... Para Instagram Reels
│   └── TikTok - Otimizados ........ Para TikTok
│
├── 📂 04 - THUMBNAILS E CAPAS
│   ├── Thumbnails YouTube ......... Para YouTube
│   ├── Thumbnails Instagram ....... Para Instagram
│   ├── Capas de E-book ............ Se aplicável
│   ├── Imagens de Produto ......... Fotos dos produtos
│   └── Arquivos Editáveis ......... PSD, Canva, etc
│
├── 📂 05 - ÁUDIO E MÚSICAS
│   ├── Músicas Livres de Direitos .. Fundo musical
│   ├── Efeitos Sonoros ............ Transições
│   ├── Narração / Voz Off ......... Locução gravada
│   └── Podcasts ................... Se tiver
│
├── 📂 06 - MATERIAIS PARA LANÇAMENTO
│   ├── Vídeos de Pré-Lançamento ... Teasers
│   ├── Vídeos de Lançamento ....... Dia do lançamento
│   ├── Vídeos de Escassez ......... "Últimas unidades"
│   ├── Vídeos de Encerramento ..... Último dia
│   └── Materiais para Anúncios .... Facebook/Google Ads
│
├── 📂 07 - LINKS COMPARTILHADOS
│   ├── Links Google Drive ......... Para clientes
│   ├── Links para Instagram Bio ... Linktree etc
│   ├── Links para WhatsApp ........ Mensagens
│   ├── Links para E-mail Marketing Mailchimp etc
│   └── Links para Anúncios Pagos .. UTM links
│
├── 📂 08 - RESULTADOS E MÉTRICAS
│   ├── Prints de Métricas ......... Screenshots
│   ├── Planilhas de Vendas ........ Controle financeiro
│   ├── Relatórios Semanais ........ Análise semanal
│   ├── Relatórios Mensais ......... Análise mensal
│   └── Prints de Depoimentos ...... Prova social
│
├── 📂 09 - MODELOS E TEMPLATES
│   ├── Templates de Vídeo ......... Reutilizáveis
│   ├── Templates de Thumbnail ...... Padronizados
│   ├── Templates de E-mail ........ E-mails prontos
│   ├── Templates de WhatsApp ...... Mensagens prontas
│   └── Templates de Instagram ...... Posts padronizados
│
└── 📂 10 - ARQUIVO E HISTÓRICO
    ├── Vídeos Antigos (backup) .... Não deletar
    ├── Roteiros Antigos ........... Referência
    ├── Campanhas Anteriores ....... O que funcionou
    └── 

💡 DICA: Numere as pastas para manter a ordem!
"""


# ========================================
# FUNÇÕES DO GOOGLE DRIVE API
# ========================================

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def autenticar_google_drive():
    """
    Autentica no Google Drive API.
    Requer arquivo 'credentials.json' na mesma pasta.
    """
    creds = None
    
    # Verificar se existe token salvo
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Se não tem credenciais válidas, fazer login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Renovando autenticação...")
            creds.refresh(Request())
        else:
            print("🔐 Iniciando autenticação no Google Drive...")
            
            if not os.path.exists('credentials.json'):
                print("\n❌ Arquivo 'credentials.json' não encontrado!")
                print("\n📥 Para obter o credentials.json:")
                print("   1. Acesse: https://console.cloud.google.com/")
                print("   2. Crie um novo projeto (ou selecione um)")
                print("   3. Ative a Google Drive API")
                print("   4. Crie credenciais OAuth 2.0")
                print("   5. Baixe o JSON e renomeie para 'credentials.json'")
                print("   6. Coloque na mesma pasta deste script")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Salvar credenciais para próxima vez
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        print("✅ Autenticação salva!")
    
    return build('drive', 'v3', credentials=creds)


def criar_pasta(service, nome_pasta, id_pai=None):
    """
    Cria uma pasta no Google Drive.
    
    Args:
        service: Serviço autenticado do Google Drive
        nome_pasta: Nome da pasta a criar
        id_pai: ID da pasta pai (None = raiz)
    
    Returns:
        ID da pasta criada
    """
    file_metadata = {
        'name': nome_pasta,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    if id_pai:
        file_metadata['parents'] = [id_pai]
    
    file = service.files().create(
        body=file_metadata,
        fields='id'
    ).execute()
    
    return file.get('id')


def criar_estrutura_recursiva(service, estrutura, id_pai=None, caminho=""):
    """
    Cria pastas recursivamente seguindo a estrutura definida.
    """
    pastas_criadas = []
    
    for nome_pasta, subpastas in estrutura.items():
        caminho_atual = f"{caminho}/{nome_pasta}" if caminho else nome_pasta
        
        # Criar a pasta
        print(f"📁 Criando: {caminho_atual}")
        
        try:
            pasta_id = criar_pasta(service, nome_pasta, id_pai)
            pastas_criadas.append({
                'nome': nome_pasta,
                'id': pasta_id,
                'caminho': caminho_atual
            })
            
            # Criar subpastas recursivamente
            if isinstance(subpastas, dict) and subpastas:
                sub_pastas = criar_estrutura_recursiva(
                    service, subpastas, pasta_id, caminho_atual
                )
                pastas_criadas.extend(sub_pastas)
            elif isinstance(subpastas, list) and subpastas:
                # Lista vazia, mas pode conter arquivos placeholder
                pass
                
        except Exception as e:
            print(f"   ⚠️  Erro ao criar '{nome_pasta}': {e}")
            continue
    
    return pastas_criadas


def listar_pasta(service, pasta_id):
    """
    Lista o conteúdo de uma pasta no Google Drive.
    """
    results = service.files().list(
        q=f"'{pasta_id}' in parents and trashed=false",
        fields="files(id, name, mimeType)",
        orderBy="name"
    ).execute()
    
    return results.get('files', [])


# ========================================
# FUNÇÃO PRINCIPAL
# ========================================

def main():
    """Função principal do organizador."""
    
    print("=" * 60)
    print("📁 NANDALIN - ORGANIZADOR DE PASTAS GOOGLE DRIVE")
    print("=" * 60)
    print()
    
    # Verificar dependências
    if not HAS_DEPS:
        print("❌ Dependências não instaladas!")
        print("\n📥 Execute:")
        print("   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        print("\n📋 Ou execute o modo manual (sem API):")
        print("   python criar_pasta_google_drive.py --manual")
        
        # Se argumento --manual, mostrar guia
        if len(sys.argv) > 1 and sys.argv[1] == '--manual':
            print(TEXTO_DESCRICAO)
            criar_arquivo_instrucoes()
        return
    
    # Verificar modo manual
    if len(sys.argv) > 1 and sys.argv[1] == '--manual':
        print(TEXTO_DESCRICAO)
        criar_arquivo_instrucoes()
        return
    
    print("Escolha uma opção:")
    print()
    print("  [1] 🔧 Criar pastas via Google Drive API (automático)")
    print("  [2] 📋 Mostrar estrutura completa (guia manual)")
    print("  [3] 📝 Gerar arquivo de instruções detalhado")
    print("  [4] 📊 Listar pastas existentes no Drive")
    print()
    
    opcao = input("Digite sua opção (1-4): ").strip()
    print()
    
    if opcao == "1":
        # Modo automático com API
        print("🚀 Iniciando criação automática...")
        print()
        
        service = autenticar_google_drive()
        
        if not service:
            print("❌ Não foi possível autenticar. Verifique o credentials.json")
            return
        
        print("✅ Autenticado com sucesso!")
        print()
        print("📁 Criando estrutura de pastas...")
        print("-" * 50)
        
        pastas_criadas = criar_estrutura_recursiva(service, ESTRUTURA_PASTAS)
        
        print("-" * 50)
        print(f"✅ Total de pastas criadas: {len(pastas_criadas)}")
        print()
        
        # Salvar IDs das pastas para referência
        salvar_referencia_pastas(pastas_criadas)
        
        print("\n💾 Referência das pastas salva em 'pastas_google_drive.json'")
        
    elif opcao == "2":
        # Mostrar guia manual
        print(TEXTO_DESCRICAO)
        
    elif opcao == "3":
        # Gerar arquivo de instruções
        criar_arquivo_instrucoes()
        
    elif opcao == "4":
        # Listar pastas existentes
        print("🔍 Conectando ao Google Drive...")
        
        service = autenticar_google_drive()
        
        if not service:
            print("❌ Não foi possível autenticar.")
            return
        
        print("\n📂 Listando pastas na raiz do Google Drive...\n")
        
        pastas = listar_pasta(service, 'root')
        
        for pasta in pastas[:20]:  # Mostrar apenas 20
            print(f"  📁 {pasta['name']}")
        
        if len(pastas) > 20:
            print(f"\n  ... e mais {len(pastas) - 20} pastas")
        
    else:
        print("❌ Opção inválida!")


def salvar_referencia_pastas(pastas_criadas):
    """
    Salva a referência das pastas criadas em JSON.
    """
    dados = {
        'data_criacao': str(__import__('datetime').datetime.now()),
        'pastas': pastas_criadas
    }
    
    with open('pastas_google_drive.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


def criar_arquivo_instrucoes():
    """
    Cria um arquivo README com instruções detalhadas
    para criar as pastas manualmente.
    """
    conteudo = """# 📁 INSTRUÇÕES - Organização Google Drive

## 🎯 Objetivo
Criar uma estrutura profissional de pastas no Google Drive
para organizar todos os vídeos de vendas da Nandalin.

---

## 📥 PASSO 1: Criar a Pasta Principal

1. Acesse [Google Drive](https://drive.google.com)
2. Clique com botão direito → **Nova pasta**
3. Nome: `📁 NANDALIN - Vídeos de Vendas`
4. Dentro dela, crie as 10 pastas numeradas abaixo

---

## 📂 PASSO 2: Criar as 10 Pastas Principais

Dentro de `📁 NANDALIN - Vídeos de Vendas`, crie:

```
📂 01 - ROTEIROS E PLANEJAMENTO
📂 02 - VÍDEOS brutos (sem edição)
📂 03 - VÍDEOS processados (após scripts)
📂 04 - THUMBNAILS E CAPAS
📂 05 - ÁUDIO E MÚSICAS
📂 06 - MATERIAIS PARA LANÇAMENTO
📂 07 - LINKS COMPARTILHADOS
📂 08 - RESULTADOS E MÉTRICAS
📂 09 - MODELOS E TEMPLATES
📂 10 - ARQUIVO E HISTÓRICO
```

---

## 📁 PASSO 3: Criar Subpastas

### 📂 01 - ROTEIROS E PLANEJAMENTO
```
├── Roteiros Prontos
├── Roteiros em Produção
├── Roteiros Finalizados
├── Planejamento Semanal
└── Calendário de Postagens
```

### 📂 02 - VÍDEOS brutos (sem edição)
```
├── Stories (9:16)
├── Completos (16:9)
├── Behind the Scenes
├── Depoimentos
└── Ensaio / Testes
```

### 📂 03 - VÍDEOS processados (após scripts)
```
├── Stories - Finalizados
├── Completos - Finalizados
├── Reels - Otimizados
└── TikTok - Otimizados
```

### 📂 04 - THUMBNAILS E CAPAS
```
├── Thumbnails YouTube
├── Thumbnails Instagram
├── Capas de E-book
├── Imagens de Produto
└── Arquivos Editáveis (PSD/Canva)
```

### 📂 05 - ÁUDIO E MÚSICAS
```
├── Músicas Livres de Direitos
├── Efeitos Sonoros
├── Narração / Voz Off
└── Podcasts
```

### 📂 06 - MATERIAIS PARA LANÇAMENTO
```
├── Vídeos de Pré-Lançamento
├── Vídeos de Lançamento
├── Vídeos de Escassez
├── Vídeos de Encerramento
└── Materiais para Anúncios
```

### 📂 07 - LINKS COMPARTILHADOS
```
├── Links Google Drive (para clientes)
├── Links para Instagram Bio
├── Links para WhatsApp
├── Links para E-mail Marketing
└── Links para Anúncios Pagos
```

### 📂 08 - RESULTADOS E MÉTRICAS
```
├── Prints de Métricas
├── Planilhas de Vendas
├── Relatórios Semanais
├── Relatórios Mensais
└── Prints de Depoimentos
```

### 📂 09 - MODELOS E TEMPLATES
```
├── Templates de Vídeo
├── Templates de Thumbnail
├── Templates de E-mail
├── Templates de Mensagem WhatsApp
└── Templates de Post Instagram
```

### 📂 10 - ARQUIVO E HISTÓRICO
```
├── Vídeos Antigos (backup)
├── Roteiros Antigos
└── Campanhas Anteriores
```

---

## 🔗 PASSO 4: Criar Links de Compartilhamento

### Para cada vídeo que for compartilhar:

1. Clique com botão direito no vídeo
2. **Compartilhar**
3. Ative **"Qualquer pessoa com o link"**
4. Permissão: **"Visualizar"** (não "Editor")
5. Copie o link

### Para criar link encurtado:

1. Acesse [bit.ly](https://bit.ly) ou [rebrandly.com](https://rebrandly.com)
2. Cole o link longo do Google Drive
3. Crie um link personalizado:
   ```
   Exemplo: bit.ly/nandalin-video-01
   ```

### Para organizar os links:

1. Na pasta `📂 07 - LINKS COMPARTILHADOS`, crie um arquivo de texto
2. Anote todos os links organizados por categoria

---

## ⚙️ PASSO 5: Configurar Permissões

### Para vídeos que VOCÊ controla:
```
Acesso: "Pessoas específicas"
Permissão: "Visualizar"
```

### Para vídeos que clientes acessam:
```
Acesso: "Qualquer pessoa com o link"
Permissão: "Visualizar"
Senha: Opcional (enviar por WhatsApp)
```

### Para vídeos VIP (após pagamento):
```
Acesso: "Pessoas específicas"
Permissão: "Visualizar"
Expiração: 7 dias
```

---

## 📱 PASSO 6: Integrar com Seus Scripts

### Após criar os vídeos com seus scripts Python:

1. Execute `processar_video.py`
2. O vídeo processado salva em `video_story_final.mp4`
3. Faça upload para a pasta correta no Drive
4. Crie o link de compartilhamento
5. Anote na pasta `📂 07 - LINKS COMPARTILHADOS`

---

## 📊 ESTRUTURA FINAL

```
📁 NANDALIN - Vídeos de Vendas
│
├── 📂 01 - ROTEIROS E PLANEJAMENTO (5 subpastas)
├── 📂 02 - VÍDEOS brutos (5 subpastas)
├── 📂 03 - VÍDEOS processados (4 subpastas)
├── 📂 04 - THUMBNAILS E CAPAS (5 subpastas)
├── 📂 05 - ÁUDIO E MÚSICAS (4 subpastas)
├── 📂 06 - MATERIAIS PARA LANÇAMENTO (5 subpastas)
├── 📂 07 - LINKS COMPARTILHADOS (5 subpastas)
├── 📂 08 - RESULTADOS E MÉTRICAS (5 subpastas)
├── 📂 09 - MODELOS E TEMPLATES (5 subpastas)
└── 📂 10 - ARQUIVO E HISTÓRICO (3 subpastas)
```

**Total:** 10 pastas principais + 46 subpastas = **56 pastas**

---

## ✅ CHECKLIST

- [ ] Criar pasta principal "NANDALIN"
- [ ] Criar 10 pastas numeradas
- [ ] Criar todas as subpastas
- [ ] Configurar permissões
- [ ] Criar links encurtados
- [ ] Testar links de compartilhamento
- [ ] Salvar referência dos links

---

## 🚀 PRÓXIMOS PASSOS

1. ✅ Criar estrutura no Drive
2. 📹 Gravar vídeos usando os roteiros
3. 🖥️ Processar com seus scripts Python
4. 📤 Upload para as pastas corretas
5. 🔗 Criar links e compartilhar
6. 📊 Acompanhar métricas

---

**Dúvidas? Consulte o arquivo `plano_marketing.md`**
"""
    
    with open('INSTRUCOES_GOOGLE_DRIVE.md', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print("✅ Arquivo 'INSTRUCOES_GOOGLE_DRIVE.md' criado!")
    print("\n📄 Abra este arquivo para ver as instruções detalhadas.")


# ========================================
# EXECUTAR
# ========================================

if __name__ == "__main__":
    main()
