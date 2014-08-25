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
    ("p3_soon","pronto"),
    ("p4_later","cuando haya tiempo"),
]

# please be extra careful when modifying STATE_CHOICES
STATE_CHOICES = [
    ("satisfy", "cumple"),
    ("fails", "no cumple"),
    ("ambiguous", "ambiguo"),
]

SECTION_CHOICES = [
    ("introduction", "Introducción"),
    ("purpose", "Introducción/Propósito"),
    ("scope", "Introducción/Alcance"),
    ("context", "Introducción/Contexto"),
    ("definitions", "Introducción/Definiciones"),
    ("references", "Introducción/Referencias"),
    ("project_members", "Equipo Desarrollador y Contraparte"),
    ("general_description", "Descripción General"),
    ("users", "Descripción General/Usuarios"),
    ("product", "Descripción General/Producto"),
    ("environment", "Descripción General/Ambiente"),
    ("related_projects", "Descripción General/Proyectos Relacionados"),
    ("design", "Diseño"),
    ("physical_architecture", "Diseño/Arquitectura Física"),
    ("logical_architecture", "Diseño/Arquitectura Lógica"),
    ("model", "Diseño/Modelo de Datos"),
    ("detailed_modules", "Diseño Detallado/Detalle Módulos"),
    ("navigation", "Diseño Detallado/Navegación"),
    ("interface", "Diseño Detallado/Interfaz"),
]

TASK_CHOICES = [
    ("t1_to_do", "por hacer"),
    ("t2_done", "realizada"),
    ("t3_not_done", "no realizada"),
    ("t4_approved", "aprobada"),
    ("t5_reprobate", "reprobada"),
    ("t6_discarded", "descartada"),
]
