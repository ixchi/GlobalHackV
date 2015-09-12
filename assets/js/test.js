var addData = function (data) {
    console.log(data);
    document.querySelector('#first_name').value = data.firstName;
    document.querySelector('#last_name').value = data.lastName;
    document.querySelector('.birthMonth').value = data.birthday.month;
    document.querySelector('.birthDate').value = data.birthday.day;
    document.querySelector('.birthYear').value = data.birthday.year;
    document.querySelector('#drivers_license_id').value = data.license;
};

var div = document.createElement('div');
div.style.position='absolute';
div.style.bottom='5px';
div.style.right='5px';
div.style.backgroundColor='lightgray';
div.style.padding='5px';
div.innerHTML = 'Demo helpers<br>';
var person1 = document.createElement('a');
person1.innerHTML = 'Fill in Carolyn Brown<br>';
person1.addEventListener('click', function(e) {
    addData({
        firstName: 'Carolyn',
        lastName: 'Brown',
        birthday: {
            year: '1980',
            month: '8',
            day: '1'
        },
        license: 'B511308400'
    });
});
div.appendChild(person1);
var person2 = document.createElement('a');
person2.innerHTML = 'Fill in Bobby Greene<br>';
person2.addEventListener('click', function(e) {
    addData({
        firstName: 'Bobby',
        lastName: 'Greene',
        birthday: {
            year: '1958',
            month: '10',
            day: '28'
        },
        license: 'D542241139'
    });
});
div.appendChild(person2);
var person3 = document.createElement('a');
person3.innerHTML = 'Fill in Bruce Roberts<br>';
person3.addEventListener('click', function(e) {
    addData({
        firstName: 'Bruce',
        lastName: 'Roberts',
        birthday: {
            year: '1966',
            month: '2',
            day: '12'
        },
        license: 'K198462046'
    });
});
div.appendChild(person3);
var person4 = document.createElement('a');
person4.innerHTML = 'Fill in Joseph Henderson<br>';
person4.addEventListener('click', function(e) {
    addData({
        firstName: 'Joseph',
        lastName: 'Henderson',
        birthday: {
            year: '1964',
            month: '4',
            day: '5'
        },
        license: 'D912386935'
    });
});
div.appendChild(person4);
document.querySelector('body').appendChild(div);
