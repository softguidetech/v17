odoo.define("thiqah.Utils", function (require) {
  "use strict";

  /**
   * Format Currency
   *
   * @param {String} value
   * @param {String} value
   */
  function formatCurrency(value) {
    let currencyFormat = new Intl.NumberFormat(undefined, {});
    return currencyFormat.format(value);
  }

  /**
   * Create chart custom backgroundColor gradient
   *
   * @param {Array,Array} colorList,labels
   * @return {Array} colorList
   */

  function generateGradients(colorList, labels, ctx, chartArea) {
    var backgroundColorList = [];
    var listOfColor = colorList;
    var i = 0,
      j = 0;
    while (i < labels.length) {
      if (j >= listOfColor.length) {
        j = 0;
      }
      backgroundColorList[i] = ctx.createLinearGradient(
        0,
        chartArea.bottom,
        0,
        chartArea.top
      );
      backgroundColorList[i].addColorStop(0, listOfColor[j][0]);
      backgroundColorList[i].addColorStop(1, listOfColor[j][1]);
      i++;
      j++;
    }
    return backgroundColorList;
  }

  /**
   * Format Number to homan readable format
   *
   * @param {String} value
   * @param {String} value
   */
  function formatCash(n) {
    if (n < 1e3) return n;
    if (n >= 1e3 && n < 1e6) return +(n / 1e3).toFixed(1) + "K";
    if (n >= 1e6 && n < 1e9) return +(n / 1e6).toFixed(1) + "M";
    if (n >= 1e9 && n < 1e12) return +(n / 1e9).toFixed(1) + "B";
    if (n >= 1e12) return +(n / 1e12).toFixed(1) + "T";
  }

  function processForm(formId){
    let form_fields = $(formId).serializeArray();
        $.each($(formId).find('input[type=file]'), function (outer_index, input) {
            $.each($(input).prop('files'), function (index, file) {
                form_fields.push({
                    name: input.name + '[' + outer_index + '][' + index + ']',
                    value: file
                });
            });
        });
        var form_values = {};
        _.each(form_fields, function (input) {
            if (input.name in form_values) {
                if (Array.isArray(form_values[input.name])) {
                    form_values[input.name].push(input.value);
                } else {
                    form_values[input.name] = [form_values[input.name], input.value];
                }
            } else {
                if (input.value !== '') {
                    form_values[input.name] = input.value;
                }
            }
        });
        return form_values;
  }

  function isValidIBANNumber(input) {
    var iban = String(input)
        .toUpperCase()
        .replace(/[^A-Z0-9]/g, ""), // keep only alphanumeric characters
      code = iban.match(/^([A-Z]{2})(\d{2})([A-Z\d]+)$/), // match and capture (1) the country code, (2) the check digits, and (3) the rest
      digits;
    // check syntax and length
    if (!code || iban.length !== CODE_LENGTHS[code[1]]) {
      return false;
    }
    // rearrange country code and check digits, and convert chars to ints
    digits = (code[3] + code[1] + code[2]).replace(
      /[A-Z]/g,
      function (letter) {
        return letter.charCodeAt(0) - 55;
      }
    );
    // final check
    return mod97(digits) === 1;
  }
  function mod97(string) {
    var checksum = string.slice(0, 2),
      fragment;
    for (var offset = 2; offset < string.length; offset += 7) {
      fragment = String(checksum) + string.substring(offset, offset + 7);
      checksum = parseInt(fragment, 10) % 97;
    }
    return checksum;
  }

  var CODE_LENGTHS = {
    AD: 24,
    AE: 23,
    AT: 20,
    AZ: 28,
    BA: 20,
    BE: 16,
    BG: 22,
    BH: 22,
    BR: 29,
    CH: 21,
    CR: 21,
    CY: 28,
    CZ: 24,
    DE: 22,
    DK: 18,
    DO: 28,
    EE: 20,
    ES: 24,
    FI: 18,
    FO: 18,
    FR: 27,
    GB: 22,
    GI: 23,
    GL: 18,
    GR: 27,
    GT: 28,
    HR: 21,
    HU: 28,
    IE: 22,
    IL: 23,
    IS: 26,
    IT: 27,
    JO: 30,
    KW: 30,
    KZ: 20,
    LB: 28,
    LI: 21,
    LT: 20,
    LU: 20,
    LV: 21,
    MC: 27,
    MD: 24,
    ME: 22,
    MK: 19,
    MR: 27,
    MT: 31,
    MU: 30,
    NL: 18,
    NO: 15,
    PK: 24,
    PL: 28,
    PS: 29,
    PT: 25,
    QA: 29,
    RO: 24,
    RS: 22,
    SA: 24,
    SE: 24,
    SI: 19,
    SK: 24,
    SM: 27,
    TN: 24,
    TR: 26,
    AL: 28,
    BY: 28,
    CR: 22,
    EG: 29,
    GE: 22,
    IQ: 23,
    LC: 32,
    SC: 31,
    ST: 25,
    SV: 28,
    TL: 23,
    UA: 29,
    VA: 22,
    VG: 24,
    XK: 20,
  };
  async function convert2DataUrl(attachments) {
    var attachmentsList = [];
    for (let i = 0; i < attachments.length; i++) {
      var reader = new FileReader();
      reader.readAsDataURL(attachments[i]);
      await new Promise((resolve) => (reader.onload = () => resolve()));
      attachmentsList.push({
        fileName: attachments[i].name,
        fileData: reader.result,
      });
    }
    return attachmentsList;
  }

  return {
    formatCurrency: formatCurrency,
    generateGradients: generateGradients,
    formatCash: formatCash,
    processForm: processForm,
    mod97:mod97,
    isValidIBANNumber:isValidIBANNumber,
    convert2DataUrl: convert2DataUrl,
  };
});
