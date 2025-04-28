document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('avaliacaoForm');
    const searchInput = document.getElementById('searchCandidato');
    const candidatoSelect = document.getElementById('nome_candidato');
    const areaAtuacaoSelect = document.getElementById('area_atuacao');

    // Busca candidatos da API
    async function loadCandidates(search = '') {
        try {
            const response = await fetch(`/api/candidatos?search=${encodeURIComponent(search)}`);
            const data = await response.json();
            
            if (data.success) {
                candidatoSelect.innerHTML = '';
                
                if (data.candidatos.length === 0) {
                    const option = document.createElement('option');
                    option.value = '';
                    option.textContent = 'Nenhum candidato encontrado';
                    candidatoSelect.appendChild(option);
                    return;
                }
                
                data.candidatos.forEach(candidato => {
                    const option = document.createElement('option');
                    option.value = candidato.nome;
                    option.textContent = candidato.nome;
                    option.dataset.area = candidato.area_atuacao;
                    candidatoSelect.appendChild(option);
                });
                
                // Atualiza área de atuação ao selecionar candidato
                candidatoSelect.addEventListener('change', function() {
                    const selectedOption = this.selectedOptions[0];
                    if (selectedOption && selectedOption.dataset.area) {
                        areaAtuacaoSelect.value = selectedOption.dataset.area;
                    }
                });
            }
        } catch (error) {
            console.error("Erro ao carregar candidatos:", error);
        }
    }

    // Configura busca de candidatos
    searchInput.addEventListener('input', function() {
        loadCandidates(this.value);
    });

    // Envio do formulário
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validação dos campos
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.style.borderColor = '#e74c3c';
                
                const errorMsg = document.createElement('p');
                errorMsg.className = 'error-message';
                errorMsg.textContent = 'Este campo é obrigatório';
                errorMsg.style.color = '#e74c3c';
                errorMsg.style.marginTop = '5px';
                
                if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('error-message')) {
                    field.parentNode.insertBefore(errorMsg, field.nextSibling);
                }
            }
        });
        
        if (!isValid) {
            alert('Por favor, preencha todos os campos obrigatórios.');
            return;
        }
        
        // Prepara os dados do formulário
        const formData = new FormData(form);
        const payload = Object.fromEntries(formData.entries());
        
        // Converte notas para números
        const camposNotas = [
            'diagnostico_problema', 'qualidade_proposta', 'conexao_objetivos',
            'uso_dados', 'clareza_apresentacao', 'protagonismo',
            'visao_futuro', 'comunicacao', 'colaboracao', 'adequacao_cultura'
        ];
        
        camposNotas.forEach(campo => {
            payload[campo] = parseInt(payload[campo]);
        });

        try {
            const response = await fetch('/api/avaliacoes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });
            
            const result = await response.json();
            
            if (result.success) {
                form.classList.add('hidden');
                document.getElementById('successMessage').classList.remove('hidden');
            } else {
                alert(`Erro: ${result.message}`);
            }
        } catch (error) {
            console.error("Erro ao enviar avaliação:", error);
            alert("Erro ao enviar avaliação. Tente novamente.");
        }
    });

    // Botão para nova avaliação
    document.getElementById('newEvaluation').addEventListener('click', function() {
        form.reset();
        form.classList.remove('hidden');
        document.getElementById('successMessage').classList.add('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Limpa mensagens de erro ao digitar
    document.querySelectorAll('[required]').forEach(field => {
        field.addEventListener('input', function() {
            if (this.value.trim()) {
                this.style.borderColor = '#ddd';
                const errorMsg = this.nextElementSibling;
                if (errorMsg && errorMsg.classList.contains('error-message')) {
                    errorMsg.remove();
                }
            }
        });
    });

    // Carrega candidatos inicialmente
    loadCandidates();
});
