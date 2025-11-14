"""
VALIDADOR DE DADOS - TERMÔMETRO DO MARANHÃO
Valida e corrige valores absurdos vindos das APIs
"""

import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """Classe para validar e corrigir dados do IBGE e outras fontes."""
    
    def __init__(self):
        # Limites sensatos para cada tipo de indicador
        self.validation_rules = {
            # Salário médio mensal (em salários mínimos)
            '29749': {
                'min': 0.5,      # Mínimo: 0.5 SM (~R$ 660)
                'max': 20,       # Máximo: 20 SM (~R$ 26.000)
                'unit': 'salários mínimos',
                'divisor': 100,  # API retorna multiplicado por 100
                'name': 'Salário médio mensal'
            },
            
            # PIB per capita (em R$)
            '47001': {
                'min': 5000,     # Mínimo: R$ 5.000
                'max': 200000,   # Máximo: R$ 200.000
                'unit': 'R$',
                'divisor': 1,    # Já vem correto geralmente
                'name': 'PIB per capita'
            },
            
            # População estimada
            '29171': {
                'min': 100,      # Mínimo: 100 habitantes
                'max': 5000000,  # Máximo: 5 milhões (São Luís)
                'unit': 'pessoas',
                'divisor': 1,
                'name': 'População estimada'
            },
            
            # Densidade demográfica (hab/km²)
            '60036': {
                'min': 0.1,
                'max': 10000,
                'unit': 'hab/km²',
                'divisor': 1,
                'name': 'Densidade demográfica'
            },
            
            # Mortalidade infantil (por mil nascidos vivos)
            '60035': {
                'min': 5,
                'max': 50,
                'unit': 'óbitos por mil nascidos vivos',
                'divisor': 1,
                'name': 'Mortalidade infantil'
            },
            
            # Taxa de escolarização (%)
            '60029': {
                'min': 50,
                'max': 100,
                'unit': '%',
                'divisor': 1,
                'name': 'Taxa de escolarização'
            },
            
            # Esgotamento sanitário adequado (%)
            '99214': {
                'min': 0,
                'max': 100,
                'unit': '% dos domicílios',
                'divisor': 1,
                'name': 'Esgotamento sanitário adequado'
            },
            
            # Área territorial (km²)
            '60028': {
                'min': 10,
                'max': 50000,
                'unit': 'km²',
                'divisor': 1,
                'name': 'Área territorial'
            }
        }
    
    def validate_and_correct(self, indicator_id, value, city_name):
        """
        Valida e corrige um valor de indicador.
        
        Args:
            indicator_id: ID do indicador (ex: '29749')
            value: Valor original (pode ser string ou número)
            city_name: Nome da cidade (para logs)
        
        Returns:
            tuple: (valor_corrigido, valor_formatado_para_exibição, é_válido)
        """
        
        if indicator_id not in self.validation_rules:
            # Se não tem regra, retorna o valor original
            return self._parse_value(value), str(value), True
        
        rules = self.validation_rules[indicator_id]
        
        # Converte para float
        try:
            numeric_value = self._parse_value(value)
            if numeric_value is None:
                return None, str(value), False
        except:
            logger.warning(f"Valor inválido para {rules['name']} em {city_name}: {value}")
            return None, str(value), False
        
        original_value = numeric_value
        
        # Aplica divisor se necessário
        if rules['divisor'] > 1:
            numeric_value = numeric_value / rules['divisor']
        
        # Verifica se está dentro dos limites
        if numeric_value < rules['min'] or numeric_value > rules['max']:
            # Tenta corrigir automaticamente
            corrected_value, corrected_display = self._auto_correct(
                numeric_value, original_value, rules, city_name
            )
            
            if corrected_value is not None:
                logger.info(
                    f"✅ CORRIGIDO: {rules['name']} em {city_name}: "
                    f"{original_value:.2f} → {corrected_value:.2f} {rules['unit']}"
                )
                return corrected_value, corrected_display, True
            else:
                logger.warning(
                    f"⚠️ VALOR FORA DO LIMITE: {rules['name']} em {city_name}: "
                    f"{numeric_value:.2f} {rules['unit']} "
                    f"(esperado: {rules['min']}-{rules['max']})"
                )
                return None, str(value), False
        
        # Valor está OK
        display_value = self._format_value(numeric_value, rules['unit'])
        return numeric_value, display_value, True
    
    def _parse_value(self, value):
        """Converte valor para float, tratando formatos brasileiros."""
        try:
            value_str = str(value).replace('.', '').replace(',', '.').replace(' ', '')
            return float(value_str)
        except:
            return None
    
    def _auto_correct(self, numeric_value, original_value, rules, city_name):
        """Tenta corrigir automaticamente valores absurdos."""
        
        # Lista de divisores comuns que podem corrigir
        possible_divisors = [10, 100, 1000, 10000]
        
        for divisor in possible_divisors:
            corrected = original_value / divisor
            if rules['min'] <= corrected <= rules['max']:
                display = self._format_value(corrected, rules['unit'])
                return corrected, display
        
        # Lista de multiplicadores (caso venha dividido)
        possible_multipliers = [10, 100, 1000]
        
        for multiplier in possible_multipliers:
            corrected = original_value * multiplier
            if rules['min'] <= corrected <= rules['max']:
                display = self._format_value(corrected, rules['unit'])
                return corrected, display
        
        # Não conseguiu corrigir
        return None, None
    
    def _format_value(self, value, unit):
        """Formata valor para exibição."""
        if 'R$' in unit:
            return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        elif '%' in unit:
            return f"{value:.1f}%"
        elif 'pessoas' in unit or 'habitantes' in unit:
            return f"{int(value):,}".replace(',', '.')
        else:
            return f"{value:.2f}"


# ========== FUNÇÃO AUXILIAR PARA USAR NO COLETOR ==========

def validate_ibge_data(indicator_id, value, city_name, indicator_name, unit):
    """
    Função helper para validar dados do IBGE.
    
    Uso:
        numeric_value, display_value, is_valid = validate_ibge_data(
            indicator_id='29749',
            value=204492288.70,
            city_name='Açailândia',
            indicator_name='Salário médio mensal',
            unit='salários mínimos'
        )
    
    Returns:
        tuple: (valor_numérico, valor_para_exibição, é_válido)
    """
    validator = DataValidator()
    return validator.validate_and_correct(indicator_id, value, city_name)


# ========== EXEMPLOS DE USO ==========

if __name__ == "__main__":
    validator = DataValidator()
    
    # Teste 1: Salário absurdo
    print("\n=== TESTE 1: Salário Absurdo ===")
    numeric, display, valid = validator.validate_and_correct(
        '29749', 
        204492288.70, 
        'Açailândia'
    )
    print(f"Resultado: {display} (válido: {valid})")
    
    # Teste 2: Salário normal
    print("\n=== TESTE 2: Salário Normal ===")
    numeric, display, valid = validator.validate_and_correct(
        '29749', 
        250.5,  # 2.5 SM (depois de dividir por 100)
        'São Luís'
    )
    print(f"Resultado: {display} (válido: {valid})")
    
    # Teste 3: População
    print("\n=== TESTE 3: População ===")
    numeric, display, valid = validator.validate_and_correct(
        '29171', 
        1108975, 
        'São Luís'
    )
    print(f"Resultado: {display} (válido: {valid})")