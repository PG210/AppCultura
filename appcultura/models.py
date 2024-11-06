from django.db import models
from .modelos.area import Area
from .modelos.departamento import Departamento
from .modelos.sectorempresa import SectorEmpresa
from .modelos.tamanioempresa import TamEmpresa
from .modelos.grupoempresa import GrupoEmpresa
from .modelos.roluser import RolUser 
from .modelos.empresa import Empresa
from .modelos.perfiluser import UserPerfil
from .modelos.cursos import Curso #cursos
from .modelos.sesioncurso import  Sesioncurso #sesiones de cursos
from .modelos.objetivoscurso import ObjetivosCurso
from .modelos.kpiarea import Kpiarea
from .modelos.kpiobjetivos import Kpiobjetivos
from .modelos.temassesion import TemasSesion
from .modelos.grupos import Grupos
from .modelos.gruposcursos import GruposCursos
from .modelos.grupouser import GruposUser
from .modelos.sesionasistencia import SesionAsistencia
from .modelos.sesionformulario import SesionFormulario
#modelos de formularios
from .modelos.formulario import Formulario
from .modelos.preguntasform import Preguntas
from .modelos.opcionform import Opciones
from .modelos.calificacionusuarios import CalificacionUsuarios

from .modelos.respuestasformulario import RespuestaForm
from .modelos.respuestaopciones import RespuestaOpciones

from .modelos.personas_compromiso import PersonasCompromisos
from .modelos.estado_compromisos import EstadoCompromisos
from .modelos.compromisos import Compromisos
# Create your models here.
from .modelos.competencias import Competencias
from .modelos.comptenciascursos import CompetenciaCurso
from .modelos.formador_empresa import FormadorEmpresa

from .modelos.calificacionformador import CalificacionFormador

#=========== avances de compromiso ====
from .modelos.avancecompromisos import AvanceCompromisos
from .modelos.fechascompromiso import FechasCompromisos

#=== intancia de la tabla accesstoken ======
from .modelos.accesstoken import AccessToken