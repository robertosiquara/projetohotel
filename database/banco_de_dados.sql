create database refugio_dos_sonhos;
use refugio_dos_sonhos;

create table clientes (
id int primary key auto_increment,
nome varchar(150) not null,
telefone int not null,
email varchar(200) unique
);

create table quartos (
numero int primary key,
tipo varchar(30) not null,
preco decimal(10,2)
);
create table reservas (
id int primary key auto_increment,
cliente_id int not null,
quarto_numero int not null,
checkin date,
checkout date,
status VARCHAR(20) DEFAULT 'ativa', 
FOREIGN KEY (cliente_id) REFERENCES clientes(id),
FOREIGN KEY (quarto_numero) REFERENCES quartos(numero)
)

