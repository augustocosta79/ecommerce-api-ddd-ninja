import time
from prometheus_client import Counter, Histogram

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total de requisições recebidas pela API",
    ["method", "endpoint", "status"]
)

HTTP_ERRORS_TOTAL = Counter(
    "http_errors_total",
    "Total de respostas com erro (HTTP 4xx e 5xx)",
    ["method", "endpoint", "status"]
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "Tempo de resposta das requisições em segundos",
    ["method", "endpoint"]
)

class PrometheusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        # Normaliza o path para evitar alta cardinalidade
        endpoint = request.resolver_match.route if request.resolver_match else request.path

        # Incrementa o contador
        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()

        if response.status_code >= 400:
            HTTP_ERRORS_TOTAL.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()

        HTTP_REQUEST_DURATION.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(duration)

        return response
