from config import db


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(10), nullable=False, default='comum')

    def __repr__(self):
        return f"<Usuario {self.nome}>"


class Fazenda(db.Model):
    __tablename__ = 'fazenda'
    id = db.Column(db.Integer, primary_key=True)
    cnpj = db.Column(db.String(20), nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))

    def __repr__(self):
        return f"<Fazenda {self.cnpj}>"


class Bovino(db.Model):
    __tablename__ = 'bovino'
    id = db.Column(db.Integer, primary_key=True)
    raca = db.Column(db.String(50))
    data_nascimento = db.Column(db.Date)
    peso = db.Column(db.Numeric(5, 2))
    fazenda_id = db.Column(db.Integer, db.ForeignKey('fazenda.id'))

    fazenda = db.relationship('Fazenda', backref=db.backref('bovinos', lazy=True))

    def __repr__(self):
        return f"<Bovino {self.raca}>"


class ESPGps(db.Model):
    __tablename__ = 'esp_gps'
    id = db.Column(db.Integer, primary_key=True)
    localizacao = db.Column(db.String(100))
    data_instalacao = db.Column(db.Date)
    bovino_id = db.Column(db.Integer, db.ForeignKey('bovino.id'))

    bovino = db.relationship('Bovino', backref=db.backref('gps', lazy=True))

    def __repr__(self):
        return f"<ESPGps {self.localizacao}>"


class SensorPosicao(db.Model):
    __tablename__ = 'sensor_posicao'
    id = db.Column(db.Integer, primary_key=True)
    esp_gps_id = db.Column(db.Integer, db.ForeignKey('esp_gps.id'))

    esp_gps = db.relationship('ESPGps', backref=db.backref('sensores_posicao', lazy=True))

    def __repr__(self):
        return f"<SensorPosicao ID {self.id}>"


class ESPPortao(db.Model):
    __tablename__ = 'esp_portao'
    id = db.Column(db.Integer, primary_key=True)
    localizacao = db.Column(db.String(100))
    data_instalacao = db.Column(db.Date)
    fazenda_id = db.Column(db.Integer, db.ForeignKey('fazenda.id'))

    fazenda = db.relationship('Fazenda', backref=db.backref('portoes', lazy=True))

    def __repr__(self):
        return f"<ESPPortao {self.localizacao}>"


class SensorDistancia(db.Model):
    __tablename__ = 'sensor_distancia'
    id = db.Column(db.Integer, primary_key=True)
    esp_portao_id = db.Column(db.Integer, db.ForeignKey('esp_portao.id'))

    esp_portao = db.relationship('ESPPortao', backref=db.backref('sensores_distancia', lazy=True))

    def __repr__(self):
        return f"<SensorDistancia ID {self.id}>"


class Buzzer(db.Model):
    __tablename__ = 'buzzer'
    id = db.Column(db.Integer, primary_key=True)
    esp_portao_id = db.Column(db.Integer, db.ForeignKey('esp_portao.id'))

    esp_portao = db.relationship('ESPPortao', backref=db.backref('buzzers', lazy=True))

    def __repr__(self):
        return f"<Buzzer ID {self.id}>"


class LED(db.Model):
    __tablename__ = 'led'
    id = db.Column(db.Integer, primary_key=True)
    esp_portao_id = db.Column(db.Integer, db.ForeignKey('esp_portao.id'))

    esp_portao = db.relationship('ESPPortao', backref=db.backref('leds', lazy=True))

    def __repr__(self):
        return f"<LED ID {self.id}>"


class SensorTemperatura(db.Model):
    __tablename__ = 'sensor_temperatura'
    id = db.Column(db.Integer, primary_key=True)
    esp_portao_id = db.Column(db.Integer, db.ForeignKey('esp_portao.id'))

    esp_portao = db.relationship('ESPPortao', backref=db.backref('sensores_temperatura', lazy=True))

    def __repr__(self):
        return f"<SensorTemperatura ID {self.id}>"
