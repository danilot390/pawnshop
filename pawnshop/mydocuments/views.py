from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.shortcuts import get_object_or_404

from mydocuments.pdf_utils import build_pdf
from mydocuments.utils import format_spanish_date
from loan.models import Pledge

from num2words import num2words

def contract_view(request, id):
    """
    This function generates a PDF document representing a contract to a loan, incorporing
    specific details fetched from the database. It retrieves loan details, constructs contract
    clauses and details based on the loan  type, & formats seller and buyer information for 
    output in the PDF.
    """
    loan = get_object_or_404(Pledge, id=id)
    client = loan.client
    owner_company = request.user.company.owner
    debt_recognition = loan.contracts.get(contract_type='DR')

    titles = [
            '<strong>DOCUMENTO PRIVADO DE VENTA CON PACTO DE RESCATE</strong>', 
            '<strong>DOCUMENTO PRIVADO DE RECONOCIMIENTO DE DEUDA Y COMPROMISO DE PAGO</strong> ',
        ]
    bodies = [
        (  f"Conste por el presente documento privado de <strong>VENTA CON PACTO DE RESCATE</strong> que a solo reconocimiento de firmas y rubricas pasara a ser documento público y con ello surtirán todos sus efectos legales, conforme a lo establecido en los arts.450 y 1297 del código civil, mismo que se suscribe bajo las siguientes clausulas:\n"
           f"<strong> PRIMERO.</strong>  (DE LAS PARTES).– El señor <strong>{client.get_full_name()}</strong>, con C.I.: <strong>{client.ci}</strong>, con domicilio en {client.address} , numero de celular {client.phone_number}, mayor de edad y consecuentemente hábil por derecho, quien en adelante se denominará VENDEDOR.\n"
           f"Por otra parte, el señor <strong>{owner_company.get_full_name()}</strong>, con C.I.:  <strong>{owner_company.ci}</strong>, mayor de edad y consecuentemente hábil por derecho, quien en adelante se denominará COMPRADOR.\n"
           f"<strong>SEGUNDO.</strong> (DEL OBJETO). - De conformidad con el art. 450 y 641 del código civil, el vendedor entrega en calidad de venta con pacto de rescate el Bien {loan.article} del cual manifiesta ser legítimo propietario, mismo que tiene las siguientes características:\n"
           f"{loan.description}\n"
           f"<strong>TERCERO.</strong> (DEL PRECIO). - El precio de libre voluntad y consentimiento por parte del vendedor, es por la suma de: {num2words(loan.loan, lang='es')} 00/100 BOLIVIANOS. (Bs.{loan.loan}.-).\n"
           f"<strong>CUARTA.</strong> (DEL PLAZO). - La fecha límite del plazo para el rescate, es el día {format_spanish_date(loan.rescue_date)}, Reservando el derecho de rescate por parte del vendedor, amparados en los arts. 644 y 645 del Código Civil."
           f"Consecuentemente en virtud de lo expuesto en la cláusula anterior la o el vendedor(a) <strong>{client.get_full_name()}</strong> tiene el derecho de rescate o de retrotraer a su dominio el mencionado bien abonando el precio convenido y las impensas acordadas dentro del plazo establecido líneas up supra, además de hacer notar de forma clara y enfática, que si el vendedor(a) no comunica al comprador <strong>{owner_company.get_full_name()}</strong> clausula y caducara su derecho, conforme a los dispuesto en el Art. 644 del Código Civil parágrafos I y II de esta manera convirtiéndose el comprador en irrevocable propietario y tener la libre disposición de la cosa, con todos los derechos que le faculta la ley.\n"
           f"<strong>QUINTA.</strong> (DE LA LEGALIDAD). - Una vez vencido el plazo el vendedor acepta expresamente al presente documento que no abra reclamo alguno, aceptando la consolidación de la venta y renunciando a recurrir a la vía judicial o extra judicial para devolución del objeto de la venta.\n"
           f"En caso de ser necesario, o surgiere algún problema o inconveniente, nosotros comprador como vendedor nos comprometemos, a realizar el debido reconocimiento de firmas y rubricas para el perfeccionamiento de la venta realizada; en caso de negativa de alguna de las partes se proseguirá a la acción legal correspondiente.\n"
           f"Así mismo el vendedor será responsable total y absoluto en caso de vender cosa ajena, conforme al art. 337(estelionato) del Código Penal.\n"
           f"<strong>SEXTA.</strong> (DE LA CONFORMIDAD). - Nosotros <strong>{client.get_full_name()}</strong> (vendedor) y el señor. <strong>{owner_company.get_full_name()}</strong> (comprador) manifestamos nuestra plena y absoluta conformidad con las clausulas suscritas en el presente contrato, haciendo notar que para la suscripción del presente contrato no ha mediado presión alguna que invalide dicho documento."),
        (
           f"Conste por el presente documento privado de reconocimiento de deuda y compromiso de pago que suscribimos abajo los firmantes y que al solo reconocimiento de firmas y rubricas surtirá efectos de instrumento público sea en la conformidad de los art 571 y 1297 del código civil, acomodado a los siguientes términos…………………………………………………………………….\n"
           f"<strong>PRIMERA.</strong> – (De las partes y monto de reconocimiento de deuda).- Yo <strong>{client.get_full_name()}</strong> con Acreedor cedula de identidad N° <strong>{client.ci}</strong>, hábil  por derecho y con capacidad jurídica y procesal plena,  domiciliado en {client.address}, a la presente sin que medie ningún vicio del consentimiento (dolo, error u violencia) a partir de la presente fecha denominado como <strong>Deudor</strong>, reconoce adeudar la suma de <strong>{debt_recognition.currency}.  {loan.loan} ({num2words(loan.loan, lang='es')} {debt_recognition.currency} 00/100)</strong> por concepto de préstamo de dinero para la compra de un vehículo, es así que reconozco nuestra <strong>DEUDA, COMPREMETIENDOME A HONRAR LA DEUDA ASUMIDA</strong> en favor del señor  <strong>{owner_company.get_full_name()}</strong> mayor de edad,  con <strong>C.I. {owner_company.ci}</strong>, vecino de esta ciudad, domiciliado en la {owner_company.address} con capacidad jurídica plena y procesal, hábil en derecho, desde la presente fecha denominado como <strong>Acreedor</strong>\n"
           f"<strong>SEGUNDA.</strong> – (Compromiso De Pago Y Fecha Perentoria De Cumplimiento De La Obligación). – De común acuerdo se estipula que la cancelación de la deuda se realizara bajo el siguiente detalle: \n"
           f"El monto de <strong>{debt_recognition.currency} {loan.loan} ({num2words(loan.loan, lang='es')} {debt_recognition.currency} 00/100)</strong> a objeto de su cancelación será computada a partir de la fecha de suscripción del presente documento, conforme a acuerdo entre partes, el deudor se compromete a realizar el pago del monto económico adeudado en fecha <strong>{format_spanish_date(debt_recognition.end_date)}</strong>\n"
           f"<strong>TERCERA.</strong> – (Mora Extrajudicial Y Garantías). – Conforme acuerdo entre partes, el deudor se compromete a cumplir y honrar la deuda hasta fecha {format_spanish_date(debt_recognition.end_date)} impostergablemente, pudiendo el acreedor instaurar la demanda ejecutiva de estructura monitoria, por parte del deudor  garantizando la deuda con todos mis bienes habidos y por haber.\n"
           f"<strong>CUARTA.</strong> – (DE LA CONFORMIDAD) Yo, <strong>{client.get_full_name()}</strong> en calidad de deudor y <strong>{owner_company.get_full_name()}</strong>  en calidad de acreedor, ambos de generales ya expresadas, firmamos al pie del presente documento en señal de conformidad de cada una de las clausulas detalladas.\n"
           f"<strong>QUINTA.</strong> – (CLAUSULA DE CONVERSION) Conste el presente documento que al solo reconocimiento de firmas y rubricas surtirá los efectos de documento público conforme a estamento legal vigente, caso contrario el mismo será sometido al correspondiente proceso de reconocimiento de firmas y rubricas. "
        )
    ]
    dates = [
        f'<strong>Potosí, {format_spanish_date(loan.loan_date)}</strong>',
        f'<strong>Potosí, {format_spanish_date(debt_recognition.initial_date)}</strong>',
    ]
    if loan.type == 'vehicles':
        purchase_vehicle = loan.contracts.get(contract_type='BS')
        titles.append('<strong>DOCUMENTO PRIVADO DE COMPRA Y VENTA DE VEHÍCULO</strong>') 
        inspection = loan.inspection
        bodies.append((
            f'Conste por el presente documento privado de COMPRA Y VENTA de un BIEN MUEBLE - <strong>VEHÍCULO</strong> de conformidad con el art. 1297 del cód. Civil, que con el solo reconocimiento de firmas y rúbricas surtirá los efectos de documento público, suscrita bajo las siguientes cláusulas y modalidades: '
	        f'\n <strong>PRIMERA.-</strong> Yo, <strong>{client.get_full_name()}, con C.I. Nº {client.ci}</strong>, mayor de edad, con capacidad jurídica plena y hábil por derecho, al presente declaro ser poseedor y Propietario de un bien mueble (VEHÍCULO) con las siguientes características:'
            f'\n <strong>Clase: </strong> AUTOMOVIL, <strong>Marca:</strong> {inspection.marca}, <strong>Tipo:</strong> {inspection.type},<strong>Modelo </strong>{inspection.model}, <strong>Motor Nº</strong> {inspection.motor},<strong>Chasis N°</strong> {inspection.chassis},<strong>Color:</strong> {inspection.color},<strong>CRPVA N°: </strong> {inspection.crpva},con <strong>placa de control:</strong> {inspection.plate} y demás características descritas en el RUAT.'
            f'\n <strong>SEGUNDA.-</strong> De conformidad con el art. 584 del cód. Civil, al presente y por así convenir de mi interés sin que medie vicio alguno de mi consentimiento y entera voluntad doy en calidad de VENTA REAL y ENAGENACÍON PERPETUA el mencionado vehículo, al señor: <strong>{owner_company.get_full_name()}, con C.I. Nº {owner_company.ci}</strong>, en la suma de <strong>{num2words(loan.loan, lang='es')} 00/100 {purchase_vehicle.currency} ({purchase_vehicle.currency}. {loan.loan}.-)</strong>, dinero que es cancelado en su totalidad a la fecha de la suscripción del presente documento. '
            f'\n <strong>TERCERA.-</strong> El VEHÍCULO objeto de la presente transferencia es libre y alodial que sobre el mismo no pesa gravamen alguno pero como transferente de buena fe salgo a la evicción y saneamiento del mismo.'
            f'\n <strong>CUARTA.-</strong> El VEHÍCULO se encuentra en funcionamiento, el cual cuenta con la aprobación del COMPRADOR, renunciando expresamente a alegar futuros reclamos.  '
            f'\n <strong>QUINTA.-</strong> Yo, <strong>{owner_company.get_full_name()}, con C.I. Nº {owner_company.ci}</strong>,  mayor de edad, con capacidad jurídica plena, en mi condición de COMPRADOR doy mi entera conformidad con todas y cada una de las cláusulas descritas en el presente documento y como muestra de ello firmo al pie del mismo.'
        ))     
        dates.append(f'<strong>Potosí, {format_spanish_date(purchase_vehicle.initial_date)}</strong>')  

    sellers_name = {'name':f'<strong>{client.get_full_name()}</strong>', 'ci':f'<strong>{client.ci}</strong>',  'foot':'<strong>VENDEDOR</strong> '}
    buyers_name =  {'name':f'<strong>{owner_company.get_full_name()}</strong>', 'ci':f'<strong>{owner_company.ci}</strong>', 'foot':'<strong>COMPRADOR</strong> '}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition']='inline: filename="contract.pdf"'
    return build_pdf(response, titles, bodies,sellers_name,buyers_name,dates)







