// Глобальные функции для работы с модальным окном
function showModal() {
    document.getElementById('description-error').innerText = '';
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

function addFilm() {
    document.getElementById('modal-title').innerText = 'Добавить фильм';
    document.getElementById('id').value = '';
    document.getElementById('title').value = '';
    document.getElementById('title-ru').value = '';
    document.getElementById('year').value = '';
    document.getElementById('description').value = '';
    showModal();
}

function sendFilm() {
    const id = document.getElementById('id').value;
    const titleRu = document.getElementById('title-ru').value.trim();
    const titleOriginal = document.getElementById('title').value.trim();
    
    if (!titleRu) {
        alert('Пожалуйста, введите русское название фильма');
        return;
    }
    
    const film = {
        title: titleOriginal,
        title_ru: titleRu,
        year: parseInt(document.getElementById('year').value) || 2024,
        description: document.getElementById('description').value.trim()
    }

    if (!film.description) {
        document.getElementById('description-error').innerText = 'Заполните описание';
        return;
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
            return{};
        }
        return resp.json();
    })
    .then(function(errors) {
        if (errors && errors.description) {
            document.getElementById('description-error').innerText = errors.description;
        } else if (document.getElementById('description-error').innerText) {
            document.getElementById('description-error').innerText = '';
        }
    })
    .catch(function(error) {
        console.error('Ошибка при сохранении фильма:', error);
        alert('Произошла ошибка при сохранении фильма');
    });
}

function editFilm(id) {
    document.getElementById('modal-title').innerText = 'Редактировать фильм';
    document.getElementById('description-error').innerText = '';
    
    fetch(`/lab7/rest-api/films/${id}`)
    .then(function(data) {
        return data.json();
    })
    .then(function (film) {
        document.getElementById('id').value = id;
        document.getElementById('title').value = film.title;
        document.getElementById('title-ru').value = film.title_ru;
        document.getElementById('year').value = film.year;
        document.getElementById('description').value = film.description;
        showModal();
    })
    .catch(function(error) {
        console.error('Ошибка при загрузке фильма для редактирования:', error);
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
    fetch('/lab7/rest-api/films/')
    .then(function(data){
        return data.json();
    })
    .then(function(films){
        let tbody = document.getElementById('film-list');
        tbody.innerHTML = '';
        
        for (let i = 0; i < films.length; i++){
            let tr = document.createElement('tr');

            // Ячейка для названия
            let tdTitle = document.createElement('td');
            let titleContainer = document.createElement('div');
            titleContainer.className = 'film-title-container';
            
            // Русское название
            let russianTitle = document.createElement('strong');
            russianTitle.innerText = films[i].title_ru;
            
            // Оригинальное название в скобках курсивом
            let originalTitle = document.createElement('span');
            originalTitle.className = 'original-title';
            
            // Показываем оригинальное название только если оно отличается от русского
            if (films[i].title && films[i].title !== films[i].title_ru) {
                originalTitle.innerText = `(${films[i].title})`;
            }
            
            titleContainer.appendChild(russianTitle);
            titleContainer.appendChild(originalTitle);
            tdTitle.appendChild(titleContainer);

            // Ячейка для года
            let tdYear = document.createElement('td');
            tdYear.innerText = films[i].year;

            // Ячейка для действий
            let tdActions = document.createElement('td');
            tdActions.style.display = 'flex';
            tdActions.style.gap = '10px';

            let editButton = document.createElement('button');
            editButton.className = 'edit';
            editButton.innerText = '✏️ Редактировать';
            editButton.onclick = function() {
                editFilm(i);
            };

            let delButton = document.createElement('button');
            delButton.className = 'delete';
            delButton.innerText = '🗑️ Удалить';
            delButton.onclick = (function(id, title) {
                return function() {
                    deleteFilm(id, title);
                };
            })(i, films[i].title_ru);

            tdActions.appendChild(editButton);
            tdActions.appendChild(delButton);

            // Добавляем ячейки в строку
            tr.appendChild(tdTitle);
            tr.appendChild(tdYear);
            tr.appendChild(tdActions);

            tbody.appendChild(tr);
        }
    })
    .catch(function(error) {
        console.error('Ошибка при загрузке фильмов:', error);
        tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: red;">Ошибка при загрузке данных</td></tr>';
    });
}