import copy

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource
# from flask import Flask
from flask import jsonify
from flask_restful.utils import cors
import json
import jsonpickle
from flask_cors import CORS, cross_origin

import random as rn


# -----------------------------------------------Cursos---------------------------------------------------
class Course:
    def __init__(self, id, cap, instructors):
        self.id = id
        self.cap = cap
        self.instructors = instructors

    def get_id(self):
        return self.id

    def get_cap(self):
        return self.cap

    def get_instructors(self):
        return self.instructors


# ----------------------------------------------Profesores--------------------------------------------------
class Instructor:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre

    def get_id(self):
        return self.id

    def get_nombre(self):
        return self.nombre


# ---------------------------------------------Salones------------------------------------------------------
class Room:
    def __init__(self, id, cap):
        self.id = id
        self.cap = cap

    def get_id(self):
        return self.id

    def get_cap(self):
        return self.cap


# --------------------------------------------Horarios De Clase--------------------------------------------
class MeetingTime:
    def __init__(self, id, time):
        self.id = id
        self.time = time

    def get_id(self):
        return self.id

    def get_time(self):
        return self.time


# -------------------------------------------Clase--------------------------------------------------
class Class:
    def __init__(self, id, R, I, MT, C):
        self.id = id
        self.R = R  # room
        self.I = I  # instructor
        self.MT = MT  # meeting time
        self.C = C  # course

    def get_id(self):
        return self.id

    def get_room(self):
        return self.R

    def get_Instructor(self):
        return self.I

    def get_MeetingTime(self):
        return self.MT

    def get_Course(self):
        return self.C

    def set_room(self, room):
        self.R = room

    def set_Instructor(self, Instructor):
        self.I = Instructor

    def set_Course(self, Course):
        self.C = Course


# ----------------------------------------Horario de un dia de Colegio -----------------------------------------------
class schedule:
    def __init__(self):
        self.clasess = []
        self.numConflicts = 0
        self.fitness = -1

    def initialize(self, r, c, mt, Nclases):
        for i in range(Nclases):
            auxc = rn.choice(c)
            auxr = rn.choice(r)
            auxi = rn.choice(auxc.instructors)
            auxmt = rn.choice(mt)
            self.clasess.append(Class(i, auxr, auxi, auxmt, auxc))

    def calculate_fitness(self):  # funcion idoneidad
        self.numConflicts = 0
        for i in range(len(self.clasess)):
            if self.clasess[i].get_room().get_cap() < self.clasess[i].get_Course().get_cap():
                self.numConflicts += 1
            for j in range(len(self.clasess)):
                if j >= i:
                    ai = self.clasess[i].get_MeetingTime().get_time()[0]
                    bj = self.clasess[j].get_MeetingTime().get_time()[0]
                    di = self.clasess[i].get_MeetingTime().get_time()[1]
                    ej = self.clasess[j].get_MeetingTime().get_time()[1]
                    idi = self.clasess[i].get_id()
                    idj = self.clasess[j].get_id()
                    if ai <= bj <= di and idi != idj or ai <= ej <= di and idi != idj:
                        if self.clasess[i].get_room().get_id() == self.clasess[j].get_room().get_id():
                            self.numConflicts += 1
                        if self.clasess[i].get_Instructor().get_id() == self.clasess[j].get_Instructor().get_id():
                            self.numConflicts += 1
        self.fitness = round(1 / (1.0 * self.numConflicts + 1), 4)

    def show_schedule(self):
        print("Numero de conflictos: {} Idonediad: {}".format(self.numConflicts, self.fitness))
        for i in range(len(self.clasess)):
            print("ID Clase: {}".format(self.clasess[i].get_id()))
            print("ID ID Aula: {}".format(self.clasess[i].get_room().get_id()))
            print("ID Profesor: {}".format(self.clasess[i].get_Instructor().get_nombre()))
            print("ID Hora: {}".format(self.clasess[i].get_MeetingTime().get_time()))
            print("ID Curso: {}".format(self.clasess[i].get_Course().get_id()))
            print()
            print()
        print('---------------------------------------------------------')


# -----------------------------------------Clase genetica---------------------------------------------------------
class schedules:
    def __init__(self, N, pMutacion, r, c, sch2, Nclases, Nhorarios):
        self.N = N
        self.rand = pMutacion
        self.Parejas = {}
        self.Individuos = sch2
        self.r = r
        self.c = c
        self.Nclases = Nclases
        self.Nhorarios = Nhorarios

    def couples(self):
        Aleatorio = rn.sample(range(self.N // 2, self.N), self.N // 2)
        self.Parejas = {}
        for i in range(self.N // 2):
            self.Parejas[i] = Aleatorio[i]
            self.Parejas[Aleatorio[i]] = i

    def sel(self):
        self.couples()
        for k, v in self.Parejas.items():
            if self.Individuos[k].fitness >= self.Individuos[v].fitness:
                self.Individuos[v] = self.Individuos[k]

    def cruce(self):
        self.couples()
        temp = 0
        for k, v in self.Parejas.items():
            if temp % 2 == 0:
                split = rn.randint(1, self.Nclases - 1)
                new1 = []
                new1[:split] = copy.deepcopy(self.Individuos[k].clasess[:split])
                new1[split:] = copy.deepcopy(self.Individuos[v].clasess[split:])
                new2 = []
                new2[:split] = copy.deepcopy(self.Individuos[v].clasess[:split])
                new2[split:] = copy.deepcopy(self.Individuos[k].clasess[split:])
                self.Individuos[k].clasess = new1
                self.Individuos[v].clasess = new2
                self.mutate(k)
                self.mutate(v)
                self.Individuos[k].calculate_fitness()
                self.Individuos[v].calculate_fitness()
            temp += 1

    def mutate(self, i):
        for j in range(len(self.Individuos[i].clasess)):
            x = self.Individuos[i].clasess[j].get_room()
            y = self.Individuos[i].clasess[j].get_Instructor()
            z = self.Individuos[i].clasess[j].get_Course()
            auxmutate = rn.choice([x, y, z])
            if auxmutate == x:
                muter = rn.choice(self.r)
            elif auxmutate == y:
                muter = rn.choice(z.instructors)
            else:
                while True:
                    muter = rn.choice(self.c)
                    auxi = rn.choice(muter.instructors)
                    # if auxi == self.Individuos[i].clasess[j].get_Instructor():
                    if auxi.id == y.id:
                        break
            if rn.random() <= self.rand:
                if auxmutate == x:
                    self.Individuos[i].clasess[j].set_room(muter)
                elif auxmutate == y:
                    self.Individuos[i].clasess[j].set_Instructor(muter)
                else:
                    self.Individuos[i].clasess[j].set_Course(muter)

    def generations(self, x, ):
        i = 0
        k = 0
        fitness_esperado = False
        while not fitness_esperado:
            if k < self.Nclases:
                if k == len(self.Individuos[k].clasess):
                    k = 0
            else:
                k = 0

            if i == x:
                break
            else:
                # print("***************************GENERACION: ", i)
                self.sel()
                self.cruce()
                # self.show()
                i += 1
                k += 1
                # print("")

            for j in range(self.Nhorarios):
                if self.Individuos[j].fitness == 1.0:
                    fitness_esperado = True

    def show(self):
        for i in range(self.N):
            print(i)
            self.Individuos[i].show_schedule()
            print("")

    def mejor_horario(self):
        return [ind for ind in self.Individuos if ind.fitness == 1.0][0]


# -----------------------------------------------Datos Iniciales-----------------------------------------------------

# ------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------
app = Flask(__name__)
# cors = CORS(app, resources={r"/*": {"origins": "*"}})
#
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# db = SQLAlchemy(app)
# ma = Marshmallow(app)
api = Api(app)


def to_dict(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))


# -----------Resources-------------------------------------------


list_salones = []
list_horas = []
list_cursos = []


class HorariosListRecource(Resource):
    @cors.crossdomain(origin='*',
                      methods={"HEAD", "OPTIONS", "GET", "POST"})
    def get(self):
        r = list_salones

        mt = list_horas

        c = list_cursos

        sch2 = []  # soluciones iniciales (Padres)
        Nhorarios = 8
        Nclases = 5

        # r1 = Room(1, 20)
        # r2 = Room(2, 25)
        # r3 = Room(3, 25)
        # r4 = Room(4, 30)
        # r5 = Room(5, 30)
        # r = [r1, r2, r3, r4, r5]
        #
        # i1 = Instructor(1, "prueba1")  # c2, c3
        # i2 = Instructor(2, "prueba2")  # c1,c2,c4
        # i3 = Instructor(3, "prueba3")  # c5,c6
        # i4 = Instructor(4, "prueba4")  # c4,c6
        # i5 = Instructor(5, "prueba5")  # c5, c3
        #
        # mt1 = MeetingTime(1, ["09:00", "11:00"])
        # mt2 = MeetingTime(2, ["08:00", "10:00"])
        # mt3 = MeetingTime(3, ["10:30", "11:30"])
        # mt4 = MeetingTime(4, ["12:00", "14:00"])
        # mt5 = MeetingTime(5, ["07:00", "09:00"])
        # mt6 = MeetingTime(6, ["13:30", "14:30"])
        # mt = [mt1, mt2, mt3, mt4, mt5, mt6]
        #
        # c1 = Course(1, 20, [i2, i4])
        # c2 = Course(2, 25, [i1, i2])
        # c3 = Course(3, 15, [i1, i5])
        # c4 = Course(4, 20, [i2, i4])
        # c5 = Course(5, 25, [i3, i5])
        # c6 = Course(6, 15, [i3, i4])
        # c7 = Course(7, 25, [i1, i2])
        # c = [c1, c2, c3, c4, c5, c6, c7]

        # sch2 = []  # soluciones iniciales (Padres)
        # Nhorarios = 8
        # Nclases = 5

        # -------------------------------------------Horarios Iniciales-------------------------------------------------------
        for i in range(Nhorarios):
            aux = schedule()
            aux.initialize(r, c, mt, Nclases)
            aux.calculate_fitness()
            sch2.append(aux)

        horarios = schedules(Nhorarios, 0.5, r, c, sch2, Nclases, Nhorarios)
        horarios.generations(50)
        # horarios.show()
        mejor = horarios.mejor_horario()

        mejor_clase = mejor.clasess

        listadict = to_dict(mejor_clase)
        return jsonify(listadict)


class SalonListResource(Resource):
    @cors.crossdomain(origin='*',
                      methods={"HEAD", "OPTIONS", "GET", "POST"})
    def get(self):
        return jsonify(to_dict(list_salones))

    def post(self):
        new_salon = Room(
            id=request.json['id'],
            cap=request.json['cap']
        )
        list_salones.append(new_salon)
        return jsonify(to_dict(list_salones))


class HorasListResource(Resource):
    @cors.crossdomain(origin='*',
                      methods={"HEAD", "OPTIONS", "GET", "POST"})

    def get(self):
        return jsonify(to_dict(list_horas))

    @cors.crossdomain(origin='*',
                      methods={"HEAD", "OPTIONS", "GET", "POST"})
    def post(self):
        new_hora = MeetingTime(
            id=request.json['id'],
            time=request.json['time']
        )
        list_horas.append(new_hora)
        return jsonify(to_dict(list_horas))


class CursosListResource(Resource):
    @cors.crossdomain(origin='*',
                      methods={"HEAD", "OPTIONS", "GET", "POST"})

    def get(self):
        return jsonify(to_dict(list_cursos))

    def post(self):

        lst = request.json['instructors']
        lst2 =[]

        for l in lst:
            lst2.append(Instructor(l["id"], l["nombre"]))


        new_curso = Course(
            id=request.json['id'],
            cap=request.json['cap'],
            instructors=lst2
        )



        list_cursos.append(new_curso)
        return jsonify(to_dict(list_cursos))


api.add_resource(HorariosListRecource, '/horarios')
api.add_resource(SalonListResource, '/salones')
api.add_resource(HorasListResource, '/horas')
api.add_resource(CursosListResource, '/cursos')

if __name__ == '__main__':
    app.run(debug=True)
