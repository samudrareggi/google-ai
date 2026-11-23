# ePlus AI Toolkit — Español

<!-- Source README.md git-blob: 2b8488a21c25e7b771f7a4014f8b945e182fe285 -->

[English](README.md) · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · **Español** · [Français](README.fr.md)

**Vista previa de macOS:** la [versión para Mac](docs/MACOS-PREVIEW.md) implementa los pasos 0–5. Los pasos de pago 2–5 pueden generar cargos reales y requieren confirmación individual; el funcionamiento real con Mac/MuMu aún no se ha verificado.

> **Documento de referencia:** [README original en inglés](README.md). Esta versión está redactada en español para que resulte más fácil de seguir, sin cambiar las instrucciones técnicas ni las advertencias. Si encuentras alguna diferencia, consulta el código y la documentación original.

**ePlus AI Toolkit** permite consultar las ofertas de Google AI Pro disponibles a través de Google One y Google Play en un dispositivo Android. Funciona en **Windows y macOS**: en Windows se inicia desde PowerShell y en Mac desde Terminal (zsh/bash). Tanto la interfaz Textual como los comandos de terminal utilizan el mismo motor basado en Python, ADB y Frida.

![Interfaz de ePlus AI Toolkit](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **Proyecto no oficial; pueden producirse cargos reales.** Los **pasos 2–5** pueden abrir un proceso de pago real de Google Play y pulsar **Subscribe** automáticamente. Encontrar una oferta, ver un precio inicial de cero o recibir un mensaje de envío del pago **no demuestra** que la cuenta cumpla los requisitos, que la suscripción sea gratuita, que esté activa ni que se haya ampliado. Antes de cada pago, comprueba en Google Play la cuenta, el importe de hoy, el precio de renovación y la siguiente fecha de cobro. Detener el programa no deshace una transacción enviada.

> [!NOTE]
> **Ten al menos 3 USD disponibles para tres operaciones separadas de 1 USD; no es un único cargo de 3 USD.** En el caso comunicado de **24 meses**, el paso 2 (12 meses iniciales), el paso 3 (+6 meses) y el paso 4 (+6 meses) corresponden a **tres operaciones de verificación de tarjeta o pago de 1 USD cada una**: **3 × US$1 = US$3**. Una operación puede ser una retención temporal de autorización y no un cargo definitivo; Google Play o el banco pueden aplicar importes distintos. **Los 3 USD son el saldo mínimo del ejemplo, no una tarifa fija ni una garantía de que cualquier cuenta obtenga los 24 meses.** Las preautorizaciones pueden reducir el saldo disponible y suelen liberarse en **1–14 días laborables**, según el banco. Comprueba tras cada paso la operación y la fecha de renovación en Google Play. El paso 5 es opcional y **no forma parte de estas tres operaciones**. [Información oficial de Google Play](https://support.google.com/googleplay/answer/6224192?hl=en).

## Descargo de responsabilidad

Este proyecto es **independiente y no está afiliado, patrocinado ni respaldado** por Google, Google One, Google Play, NetEase o MuMuPlayer. El software se ofrece **tal cual**, sin garantías de elegibilidad, resultado de suscripción o compatibilidad. Úsalo solo con cuentas y dispositivos propios o autorizados y respeta las leyes y condiciones de cada plataforma. Lee el [descargo completo (inglés)](DISCLAIMER.md) y las [precauciones de seguridad](SECURITY.md).

## 1. Preparar el entorno

**Sigue las instrucciones de tu sistema operativo.** En macOS no hace falta instalar PowerShell.

| Componente | Windows | macOS |
| --- | --- | --- |
| Terminal | **PowerShell 5.1 o posterior** | **Terminal**, con zsh o bash |
| Python | **3.10 o posterior** (comando `python`) | **3.10 o posterior** (`python3`); se crea un entorno `.venv` local |
| Git | Git para Windows | Git mediante Xcode Command Line Tools o Homebrew |
| Android | Dispositivo o emulador con root y ADB; el proyecto contempla **MuMuPlayer para Windows** | Dispositivo Android con root o emulador compatible; **MuMuPlayer Pro para Mac** es una opción para equipos Apple Silicon, no para Intel |
| Aplicaciones | Google Play Store y Google One, con la cuenta que quieres comprobar | Las mismas aplicaciones en el Android elegido |
| ADB | El programa puede localizar o descargar Android SDK Platform-Tools | Debes instalarlo por separado, por ejemplo, con `brew install android-platform-tools`; compruébalo con `adb devices` |
| Frida | **16.5.9**; la preparación de Windows puede configurarla | **16.5.9** en `.venv`; es necesario comprobar que sea compatible con Android |
| Inicio | `.\run-all.ps1` | `sh run-macos.sh` o `ePlus-AI-Toolkit.command` |

En ambos sistemas necesitas acceso autorizado a un entorno Android correctamente configurado. Aunque la implementación de macOS incluye los pasos 0–5, **no se ha probado un proceso de pago real en Mac/MuMu**. Consulta las guías de [Windows](docs/INSTALLATION.md) y [macOS](docs/MACOS-PREVIEW.md).

### Requisitos en Windows

- Windows con **PowerShell 5.1 o posterior** y **Python 3.10 o posterior**.
- MuMuPlayer instalado por tu cuenta, con root y depuración ADB activados.
- Google Play Store y Google One instalados y conectados a la cuenta que quieres consultar.
- Una conexión ADB y una versión de **Frida 16.5.9** compatible. La herramienta puede ayudarte a preparar estos componentes, pero **no instala MuMuPlayer**.

### Paso 1 — Instalar MuMuPlayer

Descarga la edición para Windows desde la [web oficial de MuMuPlayer (NetEase)](https://www.mumuplayer.com/download/). Evita los sitios de descargas no oficiales.

Inicia el emulador, activa root y ADB y verifica que Google Play Store y Google One estén disponibles. Después, inicia sesión en la cuenta de Google que vas a comprobar.

También puedes consultar la [guía ilustrada de instalación en GitHub Wiki](https://github.com/hoangsvit/google-ai/wiki/Install).

## 2. Descargar y ejecutar

En PowerShell:

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

Si ya clonaste el repositorio:

```powershell
git pull --ff-only
.\run-all.ps1
```

Al ejecutar **sin parámetros** se abre el panel Textual; no se inicia una compra automáticamente. Cuando sea necesario, el programa puede preparar Textual, ADB o Frida. Normalmente **no hace falta** ejecutar `setup_env.py` antes. La preparación puede modificar el emulador, el proxy o la configuración de red.

Si ADB está disponible en PATH, comprueba la conexión:

```powershell
adb devices
```

El estado debe ser `device`, no `offline` ni `unauthorized`. Más información en la [guía técnica](docs/DETAILED-GUIDE.md).

### Si la versión más reciente no funciona, prueba una versión publicada

Si la versión más reciente del repositorio falla, puedes probar **una versión publicada anteriormente** en [GitHub Releases](https://github.com/hoangsvit/google-ai/releases). Lee las notas y descarga el paquete de Windows **si está adjunto**. Si únicamente aparece el archivo automático **Source code (zip)** de GitHub, descárgalo, descomprímelo, abre PowerShell en la carpeta extraída y ejecuta:

```powershell
.\run-all.ps1
```

**Source code (zip) no es un `.exe` precompilado ni un instalador.** Guarda la versión publicada en **otra carpeta**, sin sobrescribir tu copia actual. Una versión anterior puede no contener las correcciones más recientes; siguen siendo necesarios Windows, Python, MuMuPlayer, ADB/Frida y las mismas precauciones sobre pagos. Si el problema continúa, consulta la [guía de solución de problemas](docs/DETAILED-GUIDE.md) o [abre una incidencia](https://github.com/hoangsvit/google-ai/issues).

## macOS — Instalación y ejecución

En macOS, instala **Git**, **Python 3.10+** y **Android SDK Platform-Tools (ADB)** (Homebrew: `brew install android-platform-tools`). Conecta un dispositivo Android con root, Google Play Store y Google One, o un emulador compatible. **MuMuPlayer Pro para Mac requiere Apple Silicon**; en Intel se necesita otro entorno Android compatible.

Abre **Terminal** y ejecuta:

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
adb devices
sh run-macos.sh
```

`sh run-macos.sh` abre el panel Textual con **pasos 0–5**. `--check` revisa el entorno (puede modificar ajustes), `--list` solo consulta ofertas y `--step 2` solo selecciona el paso, **sin pagar automáticamente**. Los pasos 2–5 pueden generar cargos reales y requieren aprobación individual. **Los pagos en un Mac/MuMu real aún no se han verificado.** Consulta la [guía Mac completa](docs/MACOS-PREVIEW.md).

## Comprobar la conexión y consultar ofertas (Windows + macOS)

El panel incorpora dos funciones de consulta inspiradas en la configuración de Android y el listado de ofertas del proyecto original:

- **Diagnose Android connection — Diagnosticar la conexión:** Comprueba si ADB está disponible, muestra los dispositivos Android autorizados, obtiene su arquitectura ABI y verifica la presencia de Google One y la versión de Frida instalada en el equipo. Ofrece instrucciones adaptadas a Windows (PowerShell, MuMu y Platform-Tools) o macOS (Terminal y Homebrew). **No instala programas, conecta ni reinicia el emulador, inicia Frida ni realiza pagos**. Ten en cuenta que `adb devices` sí puede poner en marcha el servidor ADB local.
- **Check Device & Offers (Step 1) — Comprobar dispositivo y ofertas:** Consulta las ofertas con el sistema Android/Frida existente y las muestra en **Offer Explorer**, debajo de Live Status. Solo aparecen el identificador de producto, el identificador de oferta, el primer período de facturación y si el precio inicial es cero. No se muestran tokens de ofertas o compras, datos completos de la cuenta ni información de tarjetas. Esta consulta **puede preparar el entorno Android**, así que no es una operación completamente libre de efectos secundarios.

**Que el precio inicial sea cero no significa que tengas una suscripción gratuita ni que se haya ampliado su duración.** Step 1 consulta, únicamente en modo de listado, los productos `g1.2tb.ai.subs_variant`, `g1.play.2tb.ai` y `g1.2tb.ai`. Los pasos 2–5 mantienen sus consultas específicas. Como el informe de Android no incluye todas las tarifas de los períodos posteriores, Offer Explorer indica que los precios futuros están **sin verificar**. Comprueba siempre los importes y las condiciones directamente en Google Play.

## 3. Usar el panel Textual

Mientras se ejecuta un paso, se desactivan **Check Device & Offers**, **Run** y los controles para cambiar de modo o de paso, de modo que no se inicien varias acciones a la vez. El paso 0 puede cambiar ajustes del equipo y el paso 1, aunque no realiza compras, puede preparar ADB/Frida. Antes de continuar con **Next**, comprueba el resultado en Google Play. **Detener o cerrar la aplicación no anula un pago ya enviado.**


**Check Device & Offers** ejecuta **Step 1 — Available offers**: consulta ofertas y **no inicia el pago**. Supervisa **Live Status** y **Show technical details**; 30 segundos sin nuevos mensajes no implican necesariamente un bloqueo.

En Windows, inicia sesión en Google Play con la cuenta que quieras usar antes de consultar las ofertas. Si la herramienta verifica la cuenta y encuentra la oferta de 12 meses con precio inicial cero, elige **Review 12-month checkout** para revisar y autorizar por separado solo el Step 2. Si se te solicita, introduce los datos de pago directamente en Google Play. Después, verifica allí el estado de la suscripción y la fecha de renovación.

En Windows, **Prepare MuMu** puede crear y abrir una instancia nueva de Android 15 en vertical. Introduce el correo de Google Play que se debe detectar y completa el inicio de sesión y la verificación en MuMu. Cuando aparezca la cuenta, elige **Check Device & Offers** para ejecutar el Step 1 en la instancia nueva.

En **Advanced: Run by step**:

| Modo | Acción |
| --- | --- |
| **One step only** | Ejecuta un único paso seleccionado, del 0 al 5 |
| **From selected step** | Inicia una secuencia guiada desde el paso que elijas (entre el 2 y el 5) |
| **All: Steps 2–5** | Inicia la secuencia desde el paso 2; el 5 es opcional |

| Paso | Función | Riesgo |
| --- | --- | --- |
| **0 — Environment** | Diagnóstico/preparación de Android, ADB y Frida | Sin compra; puede cambiar ajustes locales |
| **1 — Available offers** | Consulta de ofertas de Google Play | Sin compra; la preparación puede cambiar ajustes |
| **2 — Pro 12 months** | Oferta original de 12 meses | **Posible cargo real** |
| **3 — Pro +6 months** | Actualización de suscripción original | **Posible cargo real** |
| **4 — Pro +6 months (second)** | Segunda actualización de suscripción | **Posible cargo real** |
| **5 — Optional +6 months** | Actualización adicional opcional | **Posible cargo real** |

**Ejemplo comunicado de 24 meses (debe confirmarse en Google Play):**

| Paso | Duración si se aplica | Operación independiente |
| --- | --- | --- |
| **2 — Pro 12 months** | **12 meses** iniciales | **1 USD** (primera operación) |
| **3 — Pro +6 months** | **18 meses** en total | **1 USD** (segunda operación) |
| **4 — Pro +6 months (second)** | **24 meses** en total | **1 USD** (tercera operación) |
| **Total hasta el paso 4** | **24 meses, si se confirma** | **3 × US$1 = US$3**; no un pago único de 3 USD |

**El paso 5 es opcional y no se incluye en estas tres operaciones.** El plazo anunciado o una preautorización no demuestran que la ampliación se haya completado: verifica la suscripción y su renovación después de cada paso.

Los meses son **nombres históricos de los pasos**, no una garantía de ampliación. Si ya tienes una suscripción activa, **no repitas el paso 2**.

El TUI exige **aprobación explícita por cada paso de pago**. Aunque aparezca un mensaje de pago enviado, comprueba el estado real, los cargos y la renovación en [Suscripciones de Google Play](https://play.google.com/store/account/subscriptions). Pulsa **Verified in Google Play → Next** solo si has confirmado personalmente el cambio. La herramienta **no puede demostrar por sí misma** la activación.

**Detener/salir:** Stop en los pasos 0–1 solicita cancelar el proceso local. En los pasos 2–5, **Stop after this step** evita los pasos siguientes, pero **no fuerza la interrupción de un pago en curso**. **Q / Exit** espera a que acabe el paso de pago actual. **D** alterna los detalles; **R** inicia el modo seleccionado.

## 4. Comandos de PowerShell (avanzado)

**Solo para Windows.** Estos comandos utilizan PowerShell; en macOS debes usar `run-macos.sh` y las [instrucciones para Mac](docs/MACOS-PREVIEW.md). Si indicas parámetros, se abre el modo CLI en lugar del panel Textual.

**Consulta y diagnóstico, sin pago:**

```powershell
.\run-all.ps1 -Step 1
.\run-all.ps1 -Step 1 -Debug
.\run-all.ps1 -Step 0
.\run-all.ps1 -Cli
```

**Los siguientes comandos pueden iniciar pagos reales:**

```powershell
.\run-all.ps1 -Step 2
.\run-all.ps1 -Step 3
.\run-all.ps1 -Step 4
.\run-all.ps1 -Step 5
```

A diferencia del TUI, un comando individual `-Step 2..5` **no pide una segunda aprobación escrita en PowerShell**. Ejecútalo solo si realmente deseas intentar una compra y ya comprobaste las condiciones.

Secuencia guiada del CLI:

```powershell
.\run-all.ps1 -AllStages
.\run-all.ps1 -AllStages -StartStep 3
```

Confirmaciones: **1 = Continue (continuar), 2 = End run (terminar), 0 = Stop (detener)**. Comprueba Google Play antes de pasar al paso siguiente. `-StartStep 3` no demuestra que las ampliaciones anteriores hayan funcionado.

Parámetros opcionales:

```powershell
.\run-all.ps1 -Step 1 -Serial emulator-5554
.\run-all.ps1 -AllStages -Email "account@gmail.com"
```

Usa solo un número de serie mostrado por ADB. Evita `-Force`: omite la comprobación de la cuenta, **pero no modifica** la elegibilidad ni las restricciones de pago de Google.

## 5. Resultados y solución de problemas

- **MuMu/ADB no detectado:** revisa el emulador, root, ADB y los permisos del dispositivo.
- **Error de Frida:** revisa los detalles y la compatibilidad de **16.5.9** con Android.
- **Sin ofertas:** abre Google One/Play Store y vuelve a ejecutar **Step 1**.
- **Cuenta incorrecta:** verifica el perfil de Google Play; no omitas la comprobación.
- **Pago solicitado:** no confirma una suscripción nueva ni una renovación; revisa Google Play antes de repetirlo.
- **Error de seguridad de pagos (por ejemplo OR-REH-04):** detén los pasos de pago y sigue el procedimiento oficial.

Los registros están en `logs/` y los informes en `ultra0-report/`. **No compartas archivos sin ocultar correos, tokens y datos de pago.** Las pruebas automáticas de CI se ejecutan con datos simulados y **no verifican compras reales**. 
## Soporte comunitario y proyectos relacionados

Si tienes problemas para instalar o utilizar ePlus AI Toolkit, puedes contactar e intercambiar consejos con la comunidad en la [publicación de soporte y debate de ePlus en Telegram](https://t.me/eplus_news/29). Para errores reproducibles, también puedes [abrir un Issue en GitHub](https://github.com/hoangsvit/google-ai/issues). **No compartas contraseñas, códigos OTP/2FA, tokens de ofertas o compras, registros sin anonimizar ni datos de tarjetas.** No es un canal de soporte oficial de Google.

**¿No puedes acceder a la oferta de Google AI Pro?** Puedes conocer otro proyecto comunitario de ePlus.DEV: [Muse Invite Hub](https://github.com/ePlus-DEV/muse-invite-hub), donde es posible [buscar o compartir códigos de invitación de Muse](https://muse.eplus.dev/). **Muse es un servicio distinto**: sus códigos **no activan ni sustituyen** una suscripción a Google AI Pro. La disponibilidad de los códigos y los requisitos de acceso pueden variar.

## Organización del repositorio

Los scripts de inicio y los módulos Python principales siguen en la carpeta raíz para que las instrucciones existentes continúen funcionando. En Windows, utiliza `run-all.ps1`; en macOS, `run-macos.sh`.

| Archivo o carpeta | Para qué sirve |
| --- | --- |
| `run-all.ps1` | Abre el panel Textual o el modo CLI de Windows |
| `run-macos.sh`, `ePlus-AI-Toolkit.command`, `macos_runner.py` | Inicio y ejecución de los pasos 0–5 en Mac; los pagos reales no se han verificado |
| `tui.py`, `tui_core.py`, `ultra0.py`, `setup_env.py`, `device_selector.py`, `query_sku.py` | Componentes Python que utiliza actualmente la herramienta |
| [`tools/windows/`](tools/windows/README.md) | Configuración manual opcional para Windows |
| [`legacy/windows/`](legacy/windows/README.md) | Archivos .bat antiguos; algunos usan `--force` para omitir la comprobación de cuenta y pueden provocar **cargos reales** |
| `scripts/`, `assets/` | Utilidades y recursos de Android/Frida |
| `tests/`, `.github/workflows/`, `docs/` | Pruebas, GitHub Actions y documentación |

## Documentación y colaboración

[README en inglés](README.md) · [Wiki de instalación](https://github.com/hoangsvit/google-ai/wiki/Install) · [Guía detallada](docs/DETAILED-GUIDE.md) · [Pasos originales](docs/ORIGINAL-STEPS.md) · [Descargo](DISCLAIMER.md) · [Seguridad](SECURITY.md) · [Contribuir](CONTRIBUTING.md) · [Avisos de terceros](THIRD_PARTY_NOTICES.md)

La documentación incluye [estructura del proyecto](docs/PROJECT.md), [uso del panel y CLI](docs/USAGE.md), [seguridad de facturación](docs/SAFETY.md), [notas del autor](docs/AUTHOR-NOTES.md) y [normas para agentes](AGENTS.md). GitHub Actions prueba Python, PowerShell, Textual y Frida/Billing mediante simulaciones, **sin transacciones reales**. Que las pruebas de CI pasen no garantiza la compatibilidad con tu dispositivo ni que tu cuenta cumpla los requisitos.

## Créditos

**Autor original:** [@gylive](https://github.com/gylive) — [google-ultra](https://github.com/gylive/google-ultra). **Mantenedor:** [David Nguyen (@hoangsvit)](https://github.com/hoangsvit) / [ePlus.DEV](https://eplus.dev). El aviso MIT del autor original permanece en `THIRD_PARTY_NOTICES.md`.

[Centro de documentación](docs/README.md) · [Guía histórica en español](docs/i18n/README.es.md) · [Seguridad de pagos](docs/SAFETY.md)
