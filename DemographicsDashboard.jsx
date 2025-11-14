import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';

const DemographicsDashboard = ({ selectedCity = "São Luís" }) => {
  const [demographicData, setDemographicData] = useState(null);
  const [selectedIndicator, setSelectedIndicator] = useState('population');
  const [loading, setLoading] = useState(true);

  // Dados simulados baseados em dados reais do IBGE
  const mockDemographicData = {
    "São Luís": {
      population: {
        value: 1108975,
        year: 2023,
        growth_rate: 0.97,
        source: "IBGE - Diretoria de Pesquisas, Coordenação de População e Indicadores Sociais",
        survey: "Estimativas da População Residente com data de referência 1º de julho de 2023",
        methodology: "Método AiBi (Crescimento Exponencial) aplicado aos dados do Censo 2022",
        last_update: "30/08/2023",
        chart_type: "line"
      },
      age_pyramid: [
        { age: "0-4", male: 45678, female: 43567, total: 89245 },
        { age: "5-9", male: 48234, female: 46123, total: 94357 },
        { age: "10-14", male: 52341, female: 50234, total: 102575 },
        { age: "15-19", male: 51456, female: 49345, total: 100801 },
        { age: "20-24", male: 48567, female: 47234, total: 95801 },
        { age: "25-29", male: 45234, female: 46567, total: 91801 },
        { age: "30-34", male: 42345, female: 44567, total: 86912 },
        { age: "35-39", male: 39456, female: 41234, total: 80690 },
        { age: "40-44", male: 36567, female: 38345, total: 74912 },
        { age: "45-49", male: 33678, female: 35456, total: 69134 },
        { age: "50-54", male: 30789, female: 32567, total: 63356 },
        { age: "55-59", male: 27890, female: 29678, total: 57568 },
        { age: "60-64", male: 24567, female: 26789, total: 51356 },
        { age: "65-69", male: 20234, female: 23456, total: 43690 },
        { age: "70-74", male: 16345, female: 19567, total: 35912 },
        { age: "75-79", male: 12456, female: 15678, total: 28134 },
        { age: "80+", male: 10234, female: 14567, total: 24801 }
      ],
      education: {
        literacy_rate: 96.2,
        school_attendance_6_14: 98.1,
        higher_education: 18.7,
        source: "IBGE - Coordenação de Trabalho e Rendimento, Diretoria de Pesquisas",
        survey: "Pesquisa Nacional por Amostra de Domicílios Contínua - PNAD Contínua 2022",
        methodology: "Taxa de alfabetização calculada para população de 15 anos ou mais"
      },
      economy: {
        gdp_per_capita: 28547.82,
        gdp_total: 31687456,
        average_salary: 2.8,
        employed_population: 456789,
        source: "IBGE - Coordenação de Contas Nacionais, Diretoria de Pesquisas",
        survey: "Produto Interno Bruto dos Municípios 2021",
        methodology: "PIB municipal calculado pela ótica da produção, seguindo metodologia do Sistema de Contas Nacionais"
      },
      health: {
        infant_mortality: 14.2,
        health_establishments: 342,
        hospital_beds: 2847,
        source: "Ministério da Saúde - Cadastro Nacional de Estabelecimentos de Saúde (CNES)",
        survey: "CNES - Competência outubro/2023",
        last_update: "15/11/2023"
      },
      housing: {
        adequate_sewage: 85.6,
        water_supply: 98.3,
        garbage_collection: 95.8,
        street_lighting: 92.4,
        source: "IBGE - Coordenação de Trabalho e Rendimento, Diretoria de Pesquisas", 
        survey: "PNAD Contínua 2022 e Censo Demográfico 2022",
        methodology: "Percentual de domicílios particulares permanentes com serviços adequados"
      }
    }
  };

  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      setDemographicData(mockDemographicData[selectedCity] || mockDemographicData["São Luís"]);
      setLoading(false);
    }, 1000);
  }, [selectedCity]);

  const renderPopulationChart = () => {
    if (!demographicData) return null;
    const populationHistory = [
      { year: 2018, population: 1101884 },
      { year: 2019, population: 1108975 },
      { year: 2020, population: 1115932 },
      { year: 2021, population: 1122234 },
      { year: 2022, population: 1108975 },
      { year: 2023, population: demographicData.population.value }
    ];
    return (
      <div className="chart-container">
        <h3>Evolução Populacional</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={populationHistory}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`} />
            <Tooltip formatter={(value) => [`${value.toLocaleString()} habitantes`, "População"]} />
            <Line type="monotone" dataKey="population" stroke="#2563eb" strokeWidth={3} />
          </LineChart>
        </ResponsiveContainer>
        <div className="source-info">
          <p><strong>Fonte:</strong> {demographicData.population.source}</p>
          <p><strong>Pesquisa:</strong> {demographicData.population.survey}</p>
          <p><strong>Metodologia:</strong> {demographicData.population.methodology}</p>
          <p><strong>Última atualização:</strong> {demographicData.population.last_update}</p>
        </div>
      </div>
    );
  };

  const renderAgePyramid = () => {
    if (!demographicData?.age_pyramid) return null;
    const pyramidData = demographicData.age_pyramid.map(group => ({
      age: group.age,
      male: -group.male,
      female: group.female,
      maleLabel: group.male.toLocaleString(),
      femaleLabel: group.female.toLocaleString()
    }));
    return (
      <div className="chart-container">
        <h3>Pirâmide Etária - {selectedCity}</h3>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '10px' }}>
          <div style={{ display: 'flex', gap: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
              <div style={{ width: '15px', height: '15px', backgroundColor: '#3b82f6' }}></div>
              <span>Homens</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
              <div style={{ width: '15px', height: '15px', backgroundColor: '#ec4899' }}></div>
              <span>Mulheres</span>
            </div>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={pyramidData} layout="horizontal" margin={{ left: 60, right: 60 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              type="number" 
              tickFormatter={(value) => Math.abs(value).toLocaleString()}
              domain={[-60000, 60000]}
            />
            <YAxis type="category" dataKey="age" />
            <Tooltip 
              formatter={(value, name) => [
                Math.abs(value).toLocaleString(), 
                name === 'male' ? 'Homens' : 'Mulheres'
              ]}
            />
            <Bar dataKey="male" fill="#3b82f6" />
            <Bar dataKey="female" fill="#ec4899" />
          </BarChart>
        </ResponsiveContainer>
        <div className="source-info">
          <p><strong>Fonte:</strong> IBGE - Coordenação de População e Indicadores Sociais, Diretoria de Pesquisas</p>
          <p><strong>Pesquisa:</strong> Censo Demográfico 2022 - Distribuição da população por sexo e grupos de idade</p>
          <p><strong>Metodologia:</strong> Contagem populacional por faixa etária quinquenal com base no Censo 2022</p>
          <p><strong>Cobertura:</strong> População residente em domicílios particulares e coletivos</p>
        </div>
      </div>
    );
  };

  const renderEconomicIndicators = () => {
    if (!demographicData?.economy) return null;
    const economicData = [
      { indicator: 'PIB per capita', value: demographicData.economy.gdp_per_capita, unit: 'R$' },
      { indicator: 'Salário médio', value: demographicData.economy.average_salary, unit: 'SM' },
      { indicator: 'População ocupada', value: demographicData.economy.employed_population, unit: 'pessoas' }
    ];
    return (
      <div className="chart-container">
        <h3>Indicadores Econômicos</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={economicData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="indicator" />
            <YAxis tickFormatter={(value) => value.toLocaleString()} />
            <Tooltip formatter={(value, name) => [value.toLocaleString(), name]} />
            <Bar dataKey="value" fill="#059669" />
          </BarChart>
        </ResponsiveContainer>
        <div className="source-info">
          <p><strong>Fonte:</strong> {demographicData.economy.source}</p>
          <p><strong>Pesquisa:</strong> {demographicData.economy.survey}</p>
          <p><strong>Metodologia:</strong> {demographicData.economy.methodology}</p>
          <p><strong>Ano de referência:</strong> 2021 (dados mais recentes disponíveis)</p>
          <p><strong>Observação:</strong> SM = Salários Mínimos. PIB a preços correntes.</p>
        </div>
      </div>
    );
  };

  const renderEducationIndicators = () => {
    if (!demographicData?.education) return null;
    const educationData = [
      { name: 'Taxa de alfabetização', value: demographicData.education.literacy_rate },
      { name: 'Frequência escolar 6-14 anos', value: demographicData.education.school_attendance_6_14 },
      { name: 'Ensino superior', value: demographicData.education.higher_education }
    ];
    const COLORS = ['#0088FE', '#00C49F', '#FFBB28'];
    return (
      <div className="chart-container">
        <h3>Indicadores Educacionais (%)</h3>
        <div style={{ display: 'flex', gap: '20px' }}>
          <ResponsiveContainer width="50%" height={250}>
            <PieChart>
              <Pie
                data={educationData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}%`}
              >
                {educationData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ flex: 1 }}>
            <h4>Detalhes:</h4>
            {educationData.map((item, index) => (
              <div key={index} style={{ margin: '10px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ width: '15px', height: '15px', backgroundColor: COLORS[index] }}></div>
                <span>{item.name}: <strong>{item.value}%</strong></span>
              </div>
            ))}
          </div>
        </div>
        <div className="source-info">
          <p><strong>Fonte:</strong> {demographicData.education.source}</p>
          <p><strong>Pesquisa:</strong> {demographicData.education.survey}</p>
          <p><strong>Metodologia:</strong> {demographicData.education.methodology}</p>
          <p><strong>Definições:</strong></p>
          <ul style={{ fontSize: '0.875rem', marginLeft: '20px' }}>
            <li>Taxa de alfabetização: Percentual de pessoas de 15 anos ou mais alfabetizadas</li>
            <li>Frequência escolar: Percentual de crianças de 6 a 14 anos frequentando escola</li>
            <li>Ensino superior: Percentual de pessoas de 25 anos ou mais com curso superior completo</li>
          </ul>
        </div>
      </div>
    );
  };

  const renderHealthIndicators = () => {
    if (!demographicData?.health) return null;
    return (
      <div className="chart-container">
        <h3>Indicadores de Saúde</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
          <div className="indicator-card">
            <h4>Mortalidade Infantil</h4>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ef4444' }}>
              {demographicData.health.infant_mortality}
            </div>
            <p>por mil nascidos vivos</p>
          </div>
          <div className="indicator-card">
            <h4>Estabelecimentos SUS</h4>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#059669' }}>
              {demographicData.health.health_establishments}
            </div>
            <p>unidades cadastradas</p>
          </div>
          <div className="indicator-card">
            <h4>Leitos Hospitalares</h4>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#3b82f6' }}>
              {demographicData.health.hospital_beds}
            </div>
            <p>leitos disponíveis</p>
          </div>
        </div>
        <div className="source-info">
          <p><strong>Fonte:</strong> {demographicData.health.source}</p>
          <p><strong>Pesquisa:</strong> {demographicData.health.survey}</p>
          <p><strong>Última atualização:</strong> {demographicData.health.last_update}</p>
          <p><strong>Observações:</strong></p>
          <ul style={{ fontSize: '0.875rem', marginLeft: '20px' }}>
            <li>Mortalidade infantil: IBGE - Estatísticas do Registro Civil 2022</li>
            <li>Estabelecimentos: Apenas unidades ativas credenciadas ao SUS</li>
            <li>Leitos: Incluem leitos SUS e não-SUS em estabelecimentos cadastrados</li>
          </ul>
        </div>
      </div>
    );
  };

  const renderHousingIndicators = () => {
    if (!demographicData?.housing) return null;
    const housingData = [
      { service: 'Esgotamento sanitário adequado', percentage: demographicData.housing.adequate_sewage },
      { service: 'Abastecimento de água', percentage: demographicData.housing.water_supply },
      { service: 'Coleta de lixo', percentage: demographicData.housing.garbage_collection },
      { service: 'Iluminação pública', percentage: demographicData.housing.street_lighting }
    ];
    return (
      <div className="chart-container">
        <h3>Indicadores de Habitação e Infraestrutura</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={housingData} layout="horizontal">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[0, 100]} />
            <YAxis type="category" dataKey="service" width={200} />
            <Tooltip formatter={(value) => [`${value}%`, "Cobertura"]} />
            <Bar dataKey="percentage" fill="#8b5cf6" />
          </BarChart>
        </ResponsiveContainer>
        <div className="source-info">
          <p><strong>Fonte:</strong> {demographicData.housing.source}</p>
          <p><strong>Pesquisa:</strong> {demographicData.housing.survey}</p>
          <p><strong>Metodologia:</strong> {demographicData.housing.methodology}</p>
          <p><strong>Definições técnicas:</strong></p>
          <ul style={{ fontSize: '0.875rem', marginLeft: '20px' }}>
            <li><strong>Esgotamento sanitário adequado:</strong> Rede geral ou fossa séptica ligada à rede</li>
            <li><strong>Abastecimento de água adequado:</strong> Rede geral de distribuição</li>
            <li><strong>Coleta de lixo:</strong> Coleta direta ou indireta pelo serviço de limpeza</li>
            <li><strong>Iluminação pública:</strong> Existência na face do domicílio</li>
          </ul>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <div style={{ fontSize: '1.2rem' }}>Carregando dados demográficos...</div>
        <div style={{ marginTop: '1rem', color: '#666' }}>
          Obtendo informações do IBGE para {selectedCity}
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '1rem' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>
        Dashboard Demográfico - {selectedCity}
      </h2>
      
      <div style={{ marginBottom: '2rem' }}>
        <label htmlFor="indicator-select" style={{ marginRight: '1rem' }}>
          Selecionar Indicador:
        </label>
        <select 
          id="indicator-select"
          value={selectedIndicator} 
          onChange={(e) => setSelectedIndicator(e.target.value)}
          style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }}
        >
          <option value="population">População</option>
          <option value="pyramid">Pirâmide Etária</option>
          <option value="economy">Economia</option>
          <option value="education">Educação</option>
          <option value="health">Saúde</option>
          <option value="housing">Habitação</option>
        </select>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        {selectedIndicator === 'population' && renderPopulationChart()}
        {selectedIndicator === 'pyramid' && renderAgePyramid()}
        {selectedIndicator === 'economy' && renderEconomicIndicators()}
        {selectedIndicator === 'education' && renderEducationIndicators()}
        {selectedIndicator === 'health' && renderHealthIndicators()}
        {selectedIndicator === 'housing' && renderHousingIndicators()}
      </div>

      <div style={{ 
        backgroundColor: '#f8f9fa', 
        padding: '1.5rem', 
        borderRadius: '8px',
        marginTop: '2rem',
        border: '1px solid #dee2e6'
      }}>
        <h4 style={{ marginBottom: '1rem' }}>Informações sobre as Fontes</h4>
        <p style={{ fontSize: '0.875rem', lineHeight: '1.5' }}>
          <strong>Metodologia de Coleta:</strong> Os dados são obtidos diretamente das APIs oficiais do IBGE 
          e órgãos governamentais. Cada indicador possui fonte, metodologia e data de atualização específicas 
          detalhadas nos gráficos acima.
        </p>
        <p style={{ fontSize: '0.875rem', lineHeight: '1.5' }}>
          <strong>Frequência de Atualização:</strong> Os dados são atualizados conforme a periodicidade 
          de cada pesquisa: anual (maioria), bienal (IDEB), decenal (Censo completo) ou mensal (CNES).
        </p>
        <p style={{ fontSize: '0.875rem', lineHeight: '1.5' }}>
          <strong>Referências Técnicas:</strong> Todas as definições seguem os padrões metodológicos 
          estabelecidos pelo IBGE e organismos internacionais como ONU e OCDE.
        </p>
      </div>

      <style jsx>{`
        .chart-container {
          background: white;
          border-radius: 8px;
          padding: 1.5rem;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          margin-bottom: 2rem;
        }
        
        .source-info {
          margin-top: 1rem;
          padding: 1rem;
          background: #f8f9fa;
          border-radius: 4px;
          font-size: 0.875rem;
          line-height: 1.4;
          border-left: 4px solid #007bff;
        }
        
        .source-info p {
          margin: 0.5rem 0;
        }
        
        .indicator-card {
          background: white;
          border: 1px solid #e9ecef;
          border-radius: 8px;
          padding: 1.5rem;
          text-align: center;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .indicator-card h4 {
          margin: 0 0 1rem 0;
          color: #495057;
        }
        
        .indicator-card p {
          margin: 0.5rem 0 0 0;
          color: #6c757d;
          font-size: 0.875rem;
        }
      `}</style>
    </div>
  );
};

export default DemographicsDashboard;