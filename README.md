# NOTE: Núcleo de Observação da Terra

## Índice
- [Uso do Repositório](#Uso-do-Repositório)
- [Pré-requisitos](#Pré-requisitos)
- [Instalação do Git e Integração com GitHub e VSCode](#Instalação-do-Git-e-Integração-com-GitHub-e-VSCode)
- [Clonagem com GitHub Desktop](#Clonagem-com-GitHub-Desktop)
- [Uso do GitHub Desktop: commit, pull, push](#uso-do-github-desktop-commit-pull-push)
- [Fluxo de Branches](#Fluxo-de-Branches)
- [Contribuição](#Contribuição)
- [Contato e Créditos](#Contato-e-Créditos)

## Uso do repositório
Este README tem como objetivo servir de exemplo para demonstrar o uso do Git e GitHub em fluxos de trabalho de desenvolvimento de software. Ele apresenta orientações de configuração do ambiente, comandos básicos do Git, uso do GitHub Desktop e do Visual Studio Code, além de boas práticas de colaboração. A ideia é fornecer um guia prático de como configurar, clonar, versionar código e colaborar em projetos usando Git e GitHub.
- **Configuração inicial:** como instalar e configurar o Git, GitHub e VSCode no seu computador.
- **Comandos básicos:** exemplos de `commit`, `pull`, `push` e gerenciamento de branches.
- **GitHub Desktop:** instruções para clonar repositórios e realizar commits, pulls e pushes usando a interface gráfica.
- **Fluxo** de trabalho: dicas de fluxo de branches e colaboração através de pull requests.
- **Contribuição:** orientações para contribuir com o projeto e entrar em contato.

## Pré-requisitos
Antes de começar, verifique se você possui os seguintes itens instalados e configurados em seu sistema:
- **Git:** Baixe e instale o Git (versão mais recente recomendada).
- **GitHub Desktop:** Instale o GitHub Desktop para facilitar o uso do Git com interface gráfica.
- **Visual Studio Code:** Instale o VS Code como editor de código (opcional, mas recomendado).
- **Conta de desenvolvedor:** Acesso à internet para clonar e atualizar repositórios remotos.

## Instalação do Git e Integração com GitHub e VSCode
1. **Baixe e instale o Git:** Acesse o site oficial do Git e faça o download para o seu sistema operacional (Windows, macOS ou Linux). Siga as instruções de instalação padrão.
2. **Configure seu usuário Git:** Abra o terminal (Prompt de Comando, Git Bash, PowerShell ou Terminal do VS Code) e configure seu nome e e-mail de usuário com os comandos abaixo:
```ruby
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"
```
Isso garante que os commits sejam associados corretamente à sua identidade.\
3. **Instale o GitHub Desktop:** Baixe e instale o GitHub Desktop. Ele permite clonar repositórios e realizar operações de Git por meio de uma interface amigável. Ao abrir o GitHub Desktop pela primeira vez, faça login com sua conta GitHub.\
4. **Integre com o VS Code:** No VS Code, certifique-se de que a extensão GitHub Pull Requests and Issues esteja instalada (geralmente já vem por padrão). Ela facilita o gerenciamento de repositórios Git e Pull Requests diretamente do editor. Para instalar extensões, abra o **Gerenciador de Extensões** do VS Code e pesquise por “GitHub”.\
5. **Teste a instalação:** No terminal ou no VS Code, `digite git --version` e `gh --version` (se usar o GitHub CLI) para confirmar que as ferramentas estão instaladas e acessíveis.

Com isso, o Git está pronto para uso em seu computador e integrado ao GitHub e VS Code.

## Clonagem com GitHub Desktop
Para clonar este repositório usando o GitHub Desktop, siga estes passos:
1. Abra o GitHub Desktop e faça login em sua conta GitHub, se ainda não tiver feito.
2. No menu superior, clique em **File > Clone repository**.
3. Na aba “URL” ou “GitHub.com”, selecione o repositório que deseja clonar (ou cole a URL do repositório). Por exemplo: `https://github.com/seuUsuario/seuRepositorio.git`.
4. Escolha a pasta local onde deseja clonar o projeto e clique em **Clone**.

Após a clonagem, o repositório estará disponível localmente na pasta escolhida. Agora você pode abrir o projeto no VS Code ou no editor de sua preferência e começar a trabalhar.

## Quick Start (Primeiros Passos)
Após clonar o repositório, siga estes passos iniciais para configurar e executar o projeto:
1. **Abra o terminal/VS Code:** No GitHub Desktop, use a opção **Repository > Open in Visual Studio Code** ou abra o VS Code manualmente e selecione a pasta do projeto.
2. **Instale dependências:** Se o projeto usar um gerenciador de pacotes (por exemplo, Node.js), instale as dependências necessárias. Por exemplo:
```ruby
npm install
```
ou
```ruby
pip install -r requirements.txt
```
3. **Execute o projeto:** Siga as instruções específicas do projeto para executá-lo. Exemplos comuns:
```ruby
npm start    # Inicia aplicação em Node.js
dotnet run   # Para projetos .NET
```
4. **Verifique o funcionamento:** Acesse o aplicativo ou visualize o resultado para garantir que tudo esteja funcionando corretamente.\
5 **Realize alterações:** Faça pequenas mudanças de teste no código, salve e rode novamente para ver os efeitos. Isso ajuda a confirmar que o fluxo de trabalho está configurado corretamente.

## Uso do GitHub Desktop: commit, pull, push
O GitHub Desktop facilita as operações comuns de Git através de uma interface gráfica. A seguir, uma visão geral dos procedimentos básicos:
- **Commit:** Depois de fazer alterações no código, volte ao GitHub Desktop e verá os arquivos modificados na aba **Changes**. Digite uma mensagem descritiva de commit no campo apropriado e clique em **Commit to main** (ou o nome da sua branch).
- **Pull:** Para atualizar seu repositório local com as últimas mudanças do remoto, clique em **Fetch origin** ou **Pull origin** no canto superior do GitHub Desktop. Isso sincroniza seu projeto com o repositório remoto no GitHub.
- **Push:** Após realizar commits localmente, envie suas alterações para o GitHub clicando em **Push origin**. Assim seus commits ficarão armazenados no repositório remoto.
Lembre-se de commitar frequentemente e de usar mensagens claras. O GitHub Desktop mostra o status do * *push/pull* * em tempo real, facilitando a colaboração.

## Fluxo de Branches
Um bom fluxo de trabalho com branches ajuda a manter o código organizado:
- Crie uma branch separada para cada nova funcionalidade ou correção. Por exemplo:
```ruby
git checkout -b feature/minha-nova-funcionalidade
```
- Faça commits regulares na sua branch de funcionalidade.
- Para incorporar as mudanças de outras pessoas, use **Pull** ou **Fetch** no GitHub Desktop na branch principal (geralmente main ou master) e, em seguida, integre as alterações:
```ruby
git checkout main
git pull
git checkout feature/minha-nova-funcionalidade
git merge main
```
Quando sua funcionalidade estiver pronta, abra um **Pull Request** no GitHub para revisão e integração. Isso permite discutir e revisar o código antes de mesclar à branch principal.
Evite trabalhar diretamente na branch principal. Mantenha as branches organizadas e nomeadas de forma clara (ex: `feature/login`, `bugfix/corrigir-erro`).

## Contribuição
Contribuições são bem-vindas! Para colaborar com este projeto, siga as etapas abaixo:
- Fork este repositório em sua conta GitHub.
- Abra uma issue para descrever o que você pretende melhorar ou corrigir, garantindo que a ideia não esteja sendo trabalhada por outra pessoa.
- Faça um clone do seu fork localmente e crie uma branch para sua contribuição:
```ruby
git checkout -b feature/nome-da-sua-feature
```
- Realize as alterações necessárias em seu código. Teste tudo antes de prosseguir.
- **Commit:** Grave mudanças significativas com mensagens claras. Por exemplo: `git commit -m "Adiciona página de login"`
- **Push:** Envie sua branch para o GitHub: git push origin feature/nome-da-sua-feature.
- No GitHub, abra um **Pull Request** comparando sua branch com a branch principal do repositório original. Descreva suas mudanças e aguarde a revisão.

## Contato e Créditos
- **Coordenador Técnico:** Fabio Hochleitner
- **Colaboradores:**
1. Clariana Borges
2. Felipe Leal
3. Hudson Campos
4. João Teixeira
5. Léo Lotsch
6. Pedro Campos
7. Pedro Mattos
