// Глобальные переменные
let currentYear = new Date().getFullYear();

// Глобальные функции для работы с модальным окном
function showModal() {
    clearErrors();
    document.querySelector('.modal-overlay').style.display = 'block';
    document.querySelector('.modal').style.display = "block";
}

function hideModal() {
    document.querySelector('.modal').style.display = 'none';
    document.querySelector('.modal-overlay').style.display = 'none';
}

function cancel() {
    hideModal();
}

function clearErrors() {
    document.getElementById('title-error').innerText = '';
    document.getElementById('title-ru-error').innerText = '';
    document.getElementById('year-error').innerText = '';
    document.getElementById('description-error').innerText = '';
}

function showError(field, message) {
    const errorElement = document.getElementById(`${field}-error`);
    if (errorElement) {
        errorElement.innerText = message;
    }
}

function addFilm() {
    document.getElementById('modal-title').innerText = 'Добавить фильм';
    document.getElementById('id').value = '';
    document.getElementById('title').value = '';
    document.getElementById('title-ru').value = '';
    document.getElementById('year').value = currentYear;
    document.getElementById('description').value = '';
    document.getElementById('char-count').textContent = '0';
    showModal();
}

function sendFilm() {
    clearErrors();
    
    const id = document.getElementById('id').value;
    const titleRu = document.getElementById('title-ru').value.trim();
    const titleOriginal = document.getElementById('title').value.trim();
    const year = document.getElementById('year').value.trim();
    const description = document.getElementById('description').value.trim();
    
    const film = {
        title: titleOriginal,
        title_ru: titleRu,
        year: year,
        description: description
    }

    const url = `/lab7/rest-api/films/${id}`;
    const method = id === '' ? 'POST' : 'PUT';
    
    fetch(url, {
        method: method,
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(film)
    })
    .then(function(resp){
        if(resp.ok) {
            fillFilmList();
            hideModal();
            return {};
        }
        return resp.json();
    })
    .then(function(errors) {
        if (errors) {
            // Отображаем ошибки для соответствующих полей
            if (errors.title) {
                showError('title', errors.title);
            }
            if (errors.title_ru) {
                showError('title-ru', errors.title_ru);
            }
            if (errors.year) {
                showError('year', errors.year);
            }
            if (errors.description) {
                showError('description', errors.description);
            }
        }
    })
    .catch(function(error) {
        console.error('Ошибка при сохранении фильма:', error);
        alert('Произошла ошибка при сохранении фильма');
    });
}

function editFilm(id) {
    document.getElementById('modal-title').innerText = 'Редактировать фильм';
    clearErrors();
    
    fetch(`/lab7/rest-api/films/${id}`)
    .then(function(data) {
        return data.json();
    })
    .then(function (film) {
        document.getElementById('id').value = film.id;
        document.getElementById('title').value = film.title;
        document.getElementById('title-ru').value = film.title_ru;
        document.getElementById('year').value = film.year;
        document.getElementById('description').value = film.description;
        document.getElementById('char-count').textContent = film.description.length;
        showModal();
    })
    .catch(function(error) {
        console.error('Ошибка при загрузке фильма для редактирования:', error);
        alert('Не удалось загрузить данные фильма');
    });
}

function deleteFilm(id, title) {
    if(!confirm(`Вы точно хотите удалить фильм "${title}"?`)) {
        return;
    }

    fetch(`/lab7/rest-api/films/${id}`, {method: 'DELETE'})
    .then(function() {
        fillFilmList();
    })
    .catch(function(error) {
        console.error('Ошибка при удалении фильма:', error);
        alert('Произошла ошибка при удалении фильма');
    });
}

function fillFilmList() {
    document.getElementById('stats-container').style.display = 'none';
    
    fetch('/lab7/rest-api/films/')
    .then(function(data){
        return data.json();
    })
    .then(function(films){
        let tbody = document.getElementById('film-list');
        tbody.innerHTML = '';
        
        if (films.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" style="text-align: center;">Фильмов пока нет</td></tr>';
            return;
        }
        
        films.forEach(function(film) {
            let tr = document.createElement('tr');

            // Ячейка для названия
            let tdTitle = document.createElement('td');
            let titleContainer = document.createElement('div');
            titleContainer.className = 'film-title-container';
            
            // Русское название
            let russianTitle = document.createElement('strong');
            russianTitle.innerText = film.title_ru;
            
            // Оригинальное название в скобках курсивом
            let originalTitle = document.createElement('span');
            originalTitle.className = 'original-title';
            
            // Показываем оригинальное название только если оно отличается от русского
            if (film.title && film.title !== film.title_ru) {
                originalTitle.innerText = `(${film.title})`;
            }
            
            titleContainer.appendChild(russianTitle);
            titleContainer.appendChild(originalTitle);
            tdTitle.appendChild(titleContainer);

            // Ячейка для года
            let tdYear = document.createElement('td');
            tdYear.innerText = film.year;

            // Ячейка для действий
            let tdActions = document.createElement('td');
            tdActions.style.display = 'flex';
            tdActions.style.gap = '10px';

            let editButton = document.createElement('button');
            editButton.className = 'edit';
            editButton.innerText = '✏️ Редактировать';
            editButton.onclick = function() {
                editFilm(film.id);
            };

            let delButton = document.createElement('button');
            delButton.className = 'delete';
            delButton.innerText = '🗑️ Удалить';
            delButton.onclick = function() {
                deleteFilm(film.id, film.title_ru);
            };

            tdActions.appendChild(editButton);
            tdActions.appendChild(delButton);

            // Добавляем ячейки в строку
            tr.appendChild(tdTitle);
            tr.appendChild(tdYear);
            tr.appendChild(tdActions);

            tbody.appendChild(tr);
        });
    })
    .catch(function(error) {
        console.error('Ошибка при загрузке фильмов:', error);
        document.getElementById('film-list').innerHTML = 
            '<tr><td colspan="3" style="text-align: center; color: red;">Ошибка при загрузке данных</td></tr>';
    });
}

function searchFilms(query) {
    if (query.length < 2) {
        if (query.length === 0) {
            fillFilmList();
        }
        return;
    }
    
    fetch(`/lab7/rest-api/search/?q=${encodeURIComponent(query)}`)
    .then(function(response) {
        return response.json();
    })
    .then(function(films) {
        let tbody = document.getElementById('film-list');
        tbody.innerHTML = '';
        
        if (films.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" style="text-align: center;">Фильмы не найдены</td></tr>';
            return;
        }
        
        films.forEach(function(film) {
            let tr = document.createElement('tr');

            let tdTitle = document.createElement('td');
            let titleContainer = document.createElement('div');
            titleContainer.className = 'film-title-container';
            
            let russianTitle = document.createElement('strong');
            russianTitle.innerText = film.title_ru;
            
            let originalTitle = document.createElement('span');
            originalTitle.className = 'original-title';
            
            if (film.title && film.title !== film.title_ru) {
                originalTitle.innerText = `(${film.title})`;
            }
            
            titleContainer.appendChild(russianTitle);
            titleContainer.appendChild(originalTitle);
            tdTitle.appendChild(titleContainer);

            let tdYear = document.createElement('td');
            tdYear.innerText = film.year;

            let tdActions = document.createElement('td');
            tdActions.style.display = 'flex';
            tdActions.style.gap = '10px';

            let editButton = document.createElement('button');
            editButton.className = 'edit';
            editButton.innerText = '✏️ Редактировать';
            editButton.onclick = function() {
                editFilm(film.id);
            };

            let delButton = document.createElement('button');
            delButton.className = 'delete';
            delButton.innerText = '🗑️ Удалить';
            delButton.onclick = function() {
                deleteFilm(film.id, film.title_ru);
            };

            tdActions.appendChild(editButton);
            tdActions.appendChild(delButton);

            tr.appendChild(tdTitle);
            tr.appendChild(tdYear);
            tr.appendChild(tdActions);

            tbody.appendChild(tr);
        });
    })
    .catch(function(error) {
        console.error('Ошибка при поиске фильмов:', error);
    });
}

function loadStats() {
    fetch('/lab7/rest-api/stats/')
    .then(function(response) {
        return response.json();
    })
    .then(function(stats) {
        const container = document.getElementById('stats-container');
        const grid = document.getElementById('stats-grid');
        
        grid.innerHTML = `
            <div class="stat-item">
                <div class="stat-value">${stats.total_films}</div>
                <div class="stat-label">Всего фильмов</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.min_year}</div>
                <div class="stat-label">Самый ранний год</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.max_year}</div>
                <div class="stat-label">Самый поздний год</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.films_21st_century}</div>
                <div class="stat-label">Фильмы 21 века</div>
            </div>
        `;
        
        container.style.display = 'block';
    })
    .catch(function(error) {
        console.error('Ошибка при загрузке статистики:', error);
    });
}