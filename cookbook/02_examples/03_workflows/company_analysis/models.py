from typing import List, Optional

from pydantic import BaseModel, Field


class ProcurementAnalysisRequest(BaseModel):
    companies: List[str] = Field(
        ..., min_length=1, max_length=5, description="Lista de 1-5 empresas para analisar"
    )
    category_name: str = Field(
        ..., min_length=1, description="Nome da categoria para análise"
    )
    analyses_requested: List[str] = Field(
        ..., min_length=1, description="Lista de tipos de análise para realizar"
    )
    buyer_org_url: Optional[str] = Field(
        default=None, description="URL da organização compradora para contexto"
    )
    annual_spend: Optional[float] = Field(
        default=None, description="Valor de gasto anual para contexto"
    )
    region: Optional[str] = Field(default=None, description="Contexto regional")
    incumbent_suppliers: List[str] = Field(
        default_factory=list, description="Fornecedores atuais/incumbentes"
    )


class ProcurementAnalysisResponse(BaseModel):
    request: ProcurementAnalysisRequest
    company_overview: Optional[str] = None
    switching_barriers_analysis: Optional[str] = None
    pestle_analysis: Optional[str] = None
    porter_analysis: Optional[str] = None
    kraljic_analysis: Optional[str] = None
    cost_drivers_analysis: Optional[str] = None
    alternative_suppliers_analysis: Optional[str] = None
    final_report: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None


class AnalysisConfig(BaseModel):
    analysis_type: str = Field(..., description="Tipo de análise para realizar")
    max_companies: int = Field(
        default=5, description="Número máximo de empresas para analisar"
    )
    include_market_data: bool = Field(
        default=True, description="Se deve incluir dados de mercado na análise"
    )
    include_financial_data: bool = Field(
        default=True, description="Se deve incluir dados financeiros na análise"
    )


class CompanyProfile(BaseModel):
    name: str = Field(..., description="Nome da empresa")
    legal_name: Optional[str] = Field(default=None, description="Nome legal completo")
    industry: Optional[str] = Field(default=None, description="Indústria/setor")
    founded_year: Optional[int] = Field(default=None, description="Ano de fundação")
    headquarters: Optional[str] = Field(
        default=None, description="Localização da sede"
    )
    annual_revenue: Optional[float] = Field(
        default=None, description="Receita anual em USD"
    )
    employee_count: Optional[int] = Field(
        default=None, description="Número de funcionários"
    )
    market_cap: Optional[float] = Field(
        default=None, description="Capitalização de mercado em USD"
    )
    website: Optional[str] = Field(default=None, description="Site da empresa")
    description: Optional[str] = Field(default=None, description="Descrição da empresa")


class SupplierProfile(BaseModel):
    name: str = Field(..., description="Nome do fornecedor")
    website: Optional[str] = Field(default=None, description="Site do fornecedor")
    headquarters: Optional[str] = Field(
        default=None, description="Localização da sede"
    )
    geographic_coverage: List[str] = Field(
        default_factory=list, description="Áreas de cobertura geográfica"
    )
    technical_capabilities: List[str] = Field(
        default_factory=list, description="Capacidades técnicas"
    )
    certifications: List[str] = Field(
        default_factory=list, description="Certificações de qualidade"
    )
    annual_revenue: Optional[float] = Field(
        default=None, description="Receita anual em USD"
    )
    employee_count: Optional[int] = Field(
        default=None, description="Número de funcionários"
    )
    key_differentiators: List[str] = Field(
        default_factory=list, description="Principais vantagens competitivas"
    )
    financial_stability_score: Optional[int] = Field(
        default=None, ge=1, le=10, description="Pontuação de estabilidade financeira (1-10)"
    )
    suitability_score: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
        description="Pontuação de adequação aos requisitos (1-10)",
    )


class AnalysisResult(BaseModel):
    analysis_type: str = Field(..., description="Tipo de análise realizada")
    company_name: str = Field(..., description="Empresa analisada")
    category_name: str = Field(..., description="Categoria analisada")
    score: Optional[int] = Field(
        default=None, ge=1, le=9, description="Pontuação geral (escala 1-9)"
    )
    summary: Optional[str] = Field(default=None, description="Resumo da análise")
    detailed_findings: Optional[str] = Field(
        default=None, description="Achados detalhados da análise"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Principais recomendações"
    )
    risk_factors: List[str] = Field(
        default_factory=list, description="Fatores de risco identificados"
    )
    success: bool = Field(
        default=True, description="Se a análise foi concluída com sucesso"
    )
    error_message: Optional[str] = Field(
        default=None, description="Mensagem de erro se a análise falhou"
    )
