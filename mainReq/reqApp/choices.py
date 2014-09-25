# -*- encoding: utf-8 -*-

STABILITY_CHOICES = [
    ("non_negotiable", "intransable"),
    ("negotiable", "transable"),
]

UR_TYPE_CHOICES = [
    ("functional", "funcional"),
    ("quality", "calidad"),
    ("restriction", "restricción"),
]

SR_TYPE_CHOICES = [
    ("functional", "funcional"),
    ("usability", "usabilidad"),
    ("maintainability", "mantenibilidad"),
    ("performance", "rendimiento"),
    ("portability", "portabilidad"),
    ("scalability", "escalabilidad"),
    ("reliability", "confiabilidad"),
    ("interoperability", "interoperabilidad"),
    ("interface", "interacción"),
    ("operational", "operacional"),
    ("resource", "recursos"),
    ("documentation", "documentación"),
]

PRIORITY_CHOICES = [
    ("p1_urgent","urgente"),
    ("p2_normal","normal"),
    ("p3_later","si se puede"),
]

# please be extra careful when modifying STATE_CHOICES
STATE_CHOICES = [
    ("satisfy", "cumple"),
    ("fails", "no cumple"),
    ("ambiguous", "ambiguo"),
]

SECTION_CHOICES = [
    ("introduction", "Introducción"),
    ("purpose", "Propósito"),
    ("scope", "Alcance"),
    ("context", "Contexto"),
    ("definitions", "Definiciones"),
    ("references", "Referencias"),
    ("project_members", "Equipo Desarrollador y Contraparte"),
    ("general_description", "Descripción General"),
    ("users", "Usuarios"),
    ("product", "Producto"),
    ("environment", "Ambiente"),
    ("related_projects", "Proyectos Relacionados"),
    ("design", "Diseño"),
    ("physical_architecture", "Arquitectura Física"),
    ("logical_architecture", "Arquitectura Lógica"),
    ("model", "Modelo de Datos"),
    ("detailed_modules", "Detalle Módulos"),
    ("navigation", "Navegación"),
    ("interface", "Interfaz"),
]

TASK_CHOICES = [
    ("t1_to_do", "por hacer"),
    ("t2_done", "realizada"),
    ("t3_not_done", "no realizada"),
    ("t4_approved", "aprobada"),
    ("t5_reprobate", "reprobada"),
    ("t6_discarded", "descartada"),
]

SEMESTER_CHOICES = [
    ("semester_1", "Primer Semestre"),
    ("semester_2", "Segundo Semestre"),
]
