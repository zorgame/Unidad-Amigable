from .entidades import Frecuencia, MetodoAnticonceptivo, ModuloEducativo, Pregunta
from .repositorios import RepositorioMetodos, RepositorioModulos, RepositorioUnidades, RepositorioUsuarios
from .seguridad import cifrar_contrasena

ADMINISTRADOR = {
    "nombre": "Coordinación Unidad Amigable",
    "correo": "admin@ucundinamarca.edu.co",
    "contrasena": "Admin2026",
    "cargo": "Coordinador de bienestar",
}

UNIDAD = {
    "nombre": "Unidad Amigable para Adolescentes y Jóvenes",
    "ubicacion": "Bienestar Universitario, Universidad de Cundinamarca - Seccional Girardot",
    "contacto": "unidad.amigable@ucundinamarca.edu.co",
}

METODOS = [
    MetodoAnticonceptivo(
        None, "Implante subdérmico", "Hormonal", 99.9, Frecuencia.VARIOS_ANIOS,
        "Varilla flexible del tamaño de un fósforo que se coloca bajo la piel del brazo y libera progestágeno. "
        "Dura entre 3 y 5 años según la marca y se puede retirar en cualquier momento.",
        "Personas que buscan una protección muy alta y prolongada sin tener que recordar nada a diario.",
        hormonal=True,
    ),
    MetodoAnticonceptivo(
        None, "DIU hormonal", "Intrauterino", 99.8, Frecuencia.VARIOS_ANIOS,
        "Dispositivo pequeño en forma de T que se ubica dentro del útero y libera levonorgestrel. "
        "Protege entre 3 y 8 años y suele disminuir el sangrado menstrual.",
        "Quienes desean un método de larga duración y menstruaciones más ligeras.",
        hormonal=True,
    ),
    MetodoAnticonceptivo(
        None, "DIU de cobre", "Intrauterino", 99.2, Frecuencia.VARIOS_ANIOS,
        "Dispositivo en forma de T recubierto de cobre que impide la fecundación. No tiene hormonas y "
        "protege hasta 10 años. También sirve como anticoncepción de emergencia hasta 5 días después.",
        "Quienes prefieren un método sin hormonas y de muy larga duración.",
    ),
    MetodoAnticonceptivo(
        None, "Inyectable trimestral", "Hormonal", 96, Frecuencia.TRIMESTRAL,
        "Inyección de progestágeno que se aplica cada 3 meses. No contiene estrógenos.",
        "Quienes prefieren no tomar algo a diario y pueden asistir a su aplicación cada tres meses.",
        hormonal=True,
    ),
    MetodoAnticonceptivo(
        None, "Inyectable mensual", "Hormonal", 96, Frecuencia.MENSUAL,
        "Inyección combinada de estrógeno y progestágeno que se aplica una vez al mes en la fecha indicada.",
        "Quienes pueden asistir mensualmente a su aplicación y no tienen contraindicaciones para estrógenos.",
        hormonal=True, con_estrogeno=True,
    ),
    MetodoAnticonceptivo(
        None, "Píldora combinada", "Hormonal", 93, Frecuencia.DIARIA,
        "Pastilla con estrógeno y progestágeno que se toma todos los días a la misma hora. "
        "Olvidar tomas reduce su efectividad.",
        "Personas con rutina estable que pueden tomarla diariamente sin olvidos.",
        hormonal=True, con_estrogeno=True,
    ),
    MetodoAnticonceptivo(
        None, "Píldora de solo progestágeno", "Hormonal", 93, Frecuencia.DIARIA,
        "Pastilla sin estrógenos que se toma todos los días, idealmente a la misma hora.",
        "Quienes tienen contraindicaciones para estrógenos y pueden mantener una toma diaria.",
        hormonal=True,
    ),
    MetodoAnticonceptivo(
        None, "Parche anticonceptivo", "Hormonal", 93, Frecuencia.SEMANAL,
        "Parche que se pega en la piel y libera hormonas. Se cambia una vez por semana durante tres semanas "
        "y se descansa la cuarta.",
        "Quienes prefieren un método semanal en lugar de una pastilla diaria.",
        hormonal=True, con_estrogeno=True,
    ),
    MetodoAnticonceptivo(
        None, "Anillo vaginal", "Hormonal", 93, Frecuencia.MENSUAL,
        "Anillo flexible que se introduce en la vagina, permanece tres semanas y se retira una semana.",
        "Quienes se sienten cómodas con un método mensual que ellas mismas colocan.",
        hormonal=True, con_estrogeno=True,
    ),
    MetodoAnticonceptivo(
        None, "Condón masculino", "Barrera", 87, Frecuencia.CADA_RELACION,
        "Funda de látex o poliuretano que se coloca en el pene erecto antes de cualquier contacto genital. "
        "Junto con el condón femenino, es el único método que también protege frente a ITS.",
        "Todas las personas con vida sexual activa, solo o como doble protección junto a otro método.",
        protege_its=True,
    ),
    MetodoAnticonceptivo(
        None, "Condón femenino", "Barrera", 79, Frecuencia.CADA_RELACION,
        "Funda de nitrilo que se introduce en la vagina antes de la relación. Protege frente a embarazo e ITS.",
        "Quienes desean un método de barrera controlado por la persona que lo usa.",
        protege_its=True,
    ),
    MetodoAnticonceptivo(
        None, "Anticoncepción de emergencia", "Emergencia", None, Frecuencia.OCASIONAL,
        "Pastilla de levonorgestrel que se toma lo antes posible tras una relación sin protección o una falla "
        "del método, idealmente en las primeras 72 horas. No es un método de uso regular ni protege frente a ITS.",
        "Situaciones puntuales: condón roto, olvido de varias píldoras o relación sin protección.",
        hormonal=True,
    ),
]

MODULOS = [
    (
        ModuloEducativo(
            None, "Métodos anticonceptivos: lo esencial", "Anticoncepción",
            """## ¿Qué es un método anticonceptivo?

Es cualquier medicamento, dispositivo o práctica que reduce la probabilidad de un embarazo. Elegir uno es una decisión **personal, libre e informada**, y puede cambiarse cuando lo necesites.

## Grupos principales

- **Larga duración (LARC):** implante y DIU. Son los más efectivos porque no dependen de recordar nada.
- **Hormonales de corta duración:** píldora, inyectable, parche y anillo.
- **De barrera:** condón masculino y femenino. Son los únicos que también protegen frente a ITS.
- **Emergencia:** solo para situaciones puntuales, nunca como método regular.

## Uso típico vs. uso perfecto

La efectividad que verás en la aplicación corresponde al **uso típico**, es decir, cómo funciona el método en la vida real, incluyendo olvidos o errores.

## Doble protección

Combinar un método de alta efectividad con el condón protege al mismo tiempo frente al embarazo y a las infecciones de transmisión sexual.

> Antes de iniciar un método hormonal o intrauterino, consulta con el personal de salud de la Unidad Amigable.""",
            "Lectura",
        ),
        [
            ("¿Cuál de estos métodos protege también frente a las ITS?",
             ["Implante subdérmico", "Condón", "DIU de cobre", "Píldora combinada"], 1),
            ("¿Qué significa la efectividad en uso típico?",
             ["La efectividad en laboratorio", "La efectividad incluyendo olvidos y errores reales",
              "La efectividad solo en adultos", "La efectividad del primer mes"], 1),
            ("¿Qué grupo de métodos es el más efectivo?",
             ["Barrera", "Emergencia", "Larga duración (implante y DIU)", "Métodos naturales"], 2),
        ],
    ),
    (
        ModuloEducativo(
            None, "Infecciones de transmisión sexual", "Prevención de ITS",
            """## ¿Qué son las ITS?

Son infecciones que se transmiten principalmente por contacto sexual (vaginal, anal u oral). Algunas son causadas por bacterias, como la **clamidia**, la **gonorrea** y la **sífilis**, y otras por virus, como el **VIH**, el **VPH** y el **herpes genital**.

## Muchas no presentan síntomas

Una persona puede tener una ITS y no notarlo. Por eso las **pruebas periódicas** son tan importantes, aunque te sientas bien.

## Señales de alerta

- Flujo, ardor o dolor al orinar.
- Llagas, verrugas o ampollas en la zona genital.
- Dolor durante las relaciones o en la parte baja del abdomen.

## Cómo prevenirlas

1. Usar condón en todas las relaciones, de principio a fin.
2. Vacunarse contra el VPH y la hepatitis B.
3. Realizarse pruebas de VIH y sífilis de forma periódica.
4. Hablar con la pareja sobre pruebas y cuidado mutuo.

> Las bacterianas tienen tratamiento y cura; las virales tienen tratamiento para controlarlas. Diagnosticar a tiempo marca la diferencia.""",
            "Lectura",
        ),
        [
            ("¿Por qué son importantes las pruebas periódicas de ITS?",
             ["Porque todas las ITS causan fiebre", "Porque muchas ITS no presentan síntomas",
              "Porque reemplazan el uso del condón", "Porque solo se hacen una vez en la vida"], 1),
            ("¿Cuál de estas ITS puede prevenirse con una vacuna?",
             ["Gonorrea", "Sífilis", "Virus del papiloma humano (VPH)", "Clamidia"], 2),
            ("¿Qué método anticonceptivo ayuda a prevenir ITS?",
             ["Anillo vaginal", "Inyectable trimestral", "Condón", "DIU hormonal"], 2),
        ],
    ),
    (
        ModuloEducativo(
            None, "Uso correcto del condón", "Prevención",
            """## Antes de usarlo

- Revisa la **fecha de vencimiento** y que el empaque tenga aire (efecto almohada).
- Abre el sobre con los dedos, **nunca con tijeras ni con los dientes**.

## Paso a paso

1. Colócalo con el pene erecto y **antes de cualquier contacto genital**.
2. Presiona la punta para sacar el aire y desenróllalo hasta la base.
3. Después de eyacular, sujétalo por la base y retira el pene antes de perder la erección.
4. Anúdalo y deséchalo en la basura, no en el inodoro.

## Errores frecuentes

- Usar dos condones a la vez: aumenta la fricción y el riesgo de ruptura.
- Usar lubricantes a base de aceite con condones de látex: debilitan el material. Usa lubricantes a base de agua o silicona.
- Reutilizarlo: cada condón es de un solo uso.

> Si el condón se rompe, acude a la Unidad Amigable: puedes recibir anticoncepción de emergencia y orientación sobre pruebas de ITS.""",
            "Guía práctica",
        ),
        [
            ("¿Cuándo se debe colocar el condón?",
             ["Justo antes de eyacular", "Antes de cualquier contacto genital",
              "Después de iniciar la penetración", "Solo si no hay otro método"], 1),
            ("¿Qué tipo de lubricante es seguro con condones de látex?",
             ["Aceite de bebé", "Vaselina", "A base de agua o silicona", "Crema corporal"], 2),
            ("¿Qué pasa si se usan dos condones al mismo tiempo?",
             ["Protegen el doble", "Aumenta el riesgo de que se rompan", "Duran más", "No hay ningún efecto"], 1),
        ],
    ),
    (
        ModuloEducativo(
            None, "Anticoncepción de emergencia", "Anticoncepción",
            """## ¿Cuándo se usa?

Después de una relación sin protección o cuando falla el método: condón roto, olvido de varias píldoras o retraso en la aplicación del inyectable.

## Opciones

- **Pastilla de levonorgestrel:** mientras antes se tome, mejor. Se recomienda en las primeras 72 horas.
- **DIU de cobre:** colocado hasta 5 días después de la relación, es la opción más efectiva.

## Lo que debes saber

- **No es abortiva:** actúa retrasando o impidiendo la ovulación.
- **No protege frente a ITS.**
- No reemplaza un método regular; si la necesitas con frecuencia, busca asesoría para elegir uno.
- Puede alterar la fecha de tu siguiente menstruación. Si se retrasa más de una semana, realiza una prueba de embarazo.

> En Colombia tienes derecho a recibir anticoncepción de emergencia en los servicios de salud sin barreras.""",
            "Preguntas frecuentes",
        ),
        [
            ("¿En qué periodo se recomienda tomar la pastilla de emergencia?",
             ["Una semana después", "Lo antes posible, idealmente en las primeras 72 horas",
              "Solo antes de la relación", "Al mes siguiente"], 1),
            ("¿La anticoncepción de emergencia protege frente a ITS?",
             ["Sí, completamente", "Solo frente al VIH", "No", "Solo si se toma dos veces"], 2),
            ("¿Cuál es la opción de emergencia más efectiva?",
             ["DIU de cobre colocado hasta 5 días después", "Tomar dos píldoras combinadas",
              "Esperar a la menstruación", "Usar condón después"], 0),
        ],
    ),
    (
        ModuloEducativo(
            None, "Derechos sexuales y reproductivos", "Salud sexual",
            """## Tus derechos

- Decidir de forma libre e informada sobre tu cuerpo y tu sexualidad.
- Recibir información clara, veraz y sin juicios.
- Acceder a métodos anticonceptivos y a pruebas de ITS.
- Recibir atención **confidencial**: tu información no se comparte sin tu autorización.
- Vivir tu sexualidad sin violencia, presión ni discriminación.

## Servicios amigables

En Colombia existen los **Servicios de Salud Amigables para Adolescentes y Jóvenes**, pensados para que puedas consultar con confianza, en horarios accesibles y con personal capacitado.

## Consentimiento

El consentimiento es **libre, informado, específico y reversible**. Puede retirarse en cualquier momento y nunca se da bajo efectos del alcohol o con presión.

> Si vives una situación de violencia sexual, busca atención de inmediato: es una urgencia médica y tienes derecho a atención integral.""",
            "Lectura",
        ),
        [
            ("¿Qué característica debe tener el consentimiento?",
             ["Se da una vez y para siempre", "Es libre, informado y se puede retirar",
              "Se asume si hay una relación", "Lo decide la otra persona"], 1),
            ("¿La atención en salud sexual es confidencial?",
             ["No, siempre se informa a la familia", "Sí, tu información no se comparte sin autorización",
              "Solo para mayores de 25 años", "Depende del semestre"], 1),
            ("¿Qué son los Servicios de Salud Amigables?",
             ["Consultorios privados de pago", "Servicios pensados para adolescentes y jóvenes",
              "Grupos de redes sociales", "Campañas solo para colegios"], 1),
        ],
    ),
]


def poblar(
    usuarios: RepositorioUsuarios,
    unidades: RepositorioUnidades,
    modulos: RepositorioModulos,
    metodos: RepositorioMetodos,
) -> None:
    if unidades.vacia():
        unidades.crear(**UNIDAD)
    if not usuarios.existe_correo(ADMINISTRADOR["correo"]):
        usuarios.crear_administrador(
            ADMINISTRADOR["nombre"],
            ADMINISTRADOR["correo"],
            cifrar_contrasena(ADMINISTRADOR["contrasena"]),
            ADMINISTRADOR["cargo"],
        )
    if metodos.vacio():
        for metodo in METODOS:
            metodos.guardar(metodo)
    if not modulos.listar():
        for modulo, preguntas in MODULOS:
            id_modulo = modulos.guardar(modulo)
            for enunciado, opciones, respuesta in preguntas:
                modulos.agregar_pregunta(Pregunta(None, id_modulo, enunciado, opciones, respuesta))
