# ServiceMonitor para o Rundeck Exporter

O ServiceMonitor é um recurso usado pelo Prometheus Operator para descobrir e monitorar endpoints de serviços no Kubernetes. Neste caso, vamos configurar um ServiceMonitor para monitorar o Rundeck Exporter.

## Pré-requisitos

Prometheus Operator instalado no cluster Kubernetes. O Prometheus Operator é responsável por criar e gerenciar recursos de monitoramento, como o ServiceMonitor. Certifique-se de que o Prometheus Operator esteja instalado e configurado corretamente antes de prosseguir com a configuração do ServiceMonitor.

### Configurando o ServiceMonitor

1. Crie um arquivo YAML para o ServiceMonitor. Por exemplo, service-monitor.yaml.

2. Abra o arquivo service-monitor.yaml em um editor de texto e defina as seguintes informações:

```
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: meu-service-monitor
  labels:
    app: rundeck-exporter
spec:
  selector:
    matchLabels:
      app: rundeck-exporter
  endpoints:
    - port: 9620
      interval: 30s
      path: /metrics
```

Certifique-se de substituir meu-service-monitor pelo nome desejado para o ServiceMonitor. Você também pode ajustar o valor do port se o Rundeck Exporter estiver exposto em uma porta diferente.

3. Salve o arquivo service-monitor.yaml com as configurações atualizadas.

4. Use o comando kubectl para aplicar o arquivo do ServiceMonitor:

```
kubectl apply -f service-monitor.yaml -n your-namespace-rundeck
```

## Verificando o ServiceMonitor

Depois de configurar o ServiceMonitor, você pode verificar se ele está sendo corretamente detectado e monitorado pelo Prometheus Operator.

1. Verifique se o ServiceMonitor foi criado corretamente:

```
kubectl get servicemonitor meu-service-monitor
```

Isso exibirá informações sobre o ServiceMonitor criado, incluindo o nome, labels e outros detalhes.

2. Verifique se o Prometheus Operator detectou o ServiceMonitor:

```
kubectl get prometheusrules --all-namespaces
```

Isso mostrará as regras de monitoramento criadas pelo Prometheus Operator. Você deve ver uma regra relacionada ao ServiceMonitor criado.

3. Verifique se as métricas do Rundeck Exporter estão sendo coletadas pelo Prometheus:

* Acesse o Prometheus UI usando um navegador:

```
http://<prometheus-endpoint>
```

Substitua <prometheus-endpoint> pelo endereço correto do serviço do Prometheus no seu cluster Kubernetes.

* Navegue até a seção "Status" no Prometheus UI e verifique se o Rundeck Exporter é exibido como um alvo de scrape (coleta de métricas).

* Você também pode verificar se as métricas estão sendo coletadas corretamente executando consultas no Prometheus para as métricas específicas do Rundeck Exporter.

## Considerações Finais

Com o ServiceMonitor configurado corretamente, o Prometheus Operator agora será capaz de monitorar o Rundeck Exporter e coletar métricas para análise e visualização no Prometheus.

Lembre-se de que é necessário ter as configurações adequadas do Rundeck Exporter, como a porta e o caminho das métricas, para que o ServiceMonitor funcione corretamente.

Certifique-se de ajustar as informações da documentação, como o nome do ServiceMonitor e outros detalhes, de acordo com a sua configuração específica.

Espero que esta documentação ajude a configurar o ServiceMonitor para o Rundeck Exporter. Se você tiver mais perguntas, fique à vontade para perguntar. Estou aqui para ajudar!
