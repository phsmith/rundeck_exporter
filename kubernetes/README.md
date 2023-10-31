# Rundeck Exporter Helm Chart

Este é um projeto de Helm Chart para implantar o Rundeck Exporter no Kubernetes.

## Descrição

O Rundeck Exporter foi desenvolvido por Phillipe Smith e é parte da contribuição da comunidade do Rundeck, é uma ferramenta que coleta métricas e informações do Rundeck para fins de monitoramento e observabilidade utilizando o Prometheus e o Grafana para exibição de dados de forma amigável. Este Chart facilita a implantação e configuração do Rundeck Exporter em um cluster Kubernetes.

## Pré-requisitos

- Um cluster Kubernetes em funcionamento.
- Rundeck, Prometheus e Grafana.
- Helm 3 ou superior instalado.

## Instalação

1. Faça o clone do repositório

```
git clone https://github.com/nataliagranato/rundeck_exporter.git
```

2. Acesse o diretório kubernetes

```
cd kubernetes
```

3. Crie a namespace (caso não exista):

```
kubectl create namespace minha-namespace
```

4. Instale o Rundeck Exporter:

```
helm install rundeck-exporter -n sua-namespace .
```

## Configuração

A configuração do Rundeck Exporter pode ser personalizada editando o arquivo values.yaml ou usando a opção --set durante a instalação.

Aqui estão algumas configurações comuns:

'image.repository': O repositório da imagem do Rundeck Exporter.
'image.tag': A tag da imagem do Rundeck Exporter.
'replicaCount': O número de réplicas desejado para o Rundeck Exporter.
'service.port': A porta em que o Rundeck Exporter expõe as métricas.
'env': Variáveis de ambiente para configurar o Rundeck Exporter.

Consulte o arquivo values.yaml para ver todas as opções de configuração disponíveis.

## Personalização

Você pode personalizar ainda mais a implantação do Rundeck Exporter editando o arquivo deployment.yaml no diretório templates. Aqui você pode adicionar volumes, definir recursos, configurar sondas de prontidão e vitalidade, entre outras opções.

## Remoção

Para remover o Rundeck Exporter, execute o seguinte comando:

```
helm uninstall rundeck-exporter

```

Isso removerá todos os recursos relacionados ao Rundeck Exporter do cluster Kubernetes.
