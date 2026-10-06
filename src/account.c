/* Educational account CLI. All amounts are integer cents. */
#include <ctype.h>
#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int parse_amount(const char *text, int64_t *amount) {
    if (!*text) return 0;
    for (const char *c = text; *c; ++c)
        if (!isdigit((unsigned char)*c)) return 0;
    errno = 0;
    char *end;
    intmax_t value = strtoimax(text, &end, 10);
    if (errno == ERANGE || *end || value > INT64_MAX || value == 0) return 0;
    *amount = (int64_t)value;
    return 1;
}

static void report(const char *status, const char *code, int64_t balance) {
    printf("{\"status\":\"%s\",\"code\":\"%s\",\"balance_cents\":%" PRId64 "}\n",
           status, code, balance);
}

int main(void) {
    int64_t balance = 0;
    int failed = 0;
    char line[256];
    while (fgets(line, sizeof line, stdin)) {
        /* Drain an oversized line so its suffix cannot become a command. */
        if (!strchr(line, '\n') && strlen(line) == sizeof line - 1) {
            int c;
            while ((c = getchar()) != '\n' && c != EOF) {}
            report("error", "line_too_long", balance);
            failed = 1;
            continue;
        }
        char *command = strtok(line, " \t\r\n");
        if (!command) continue;
        char *argument = strtok(NULL, " \t\r\n");
        char *extra = strtok(NULL, " \t\r\n");
        const char *error = NULL;
        int64_t amount = 0;
        if (!strcmp(command, "balance")) {
            if (argument) error = "invalid_arguments";
        } else if (!strcmp(command, "deposit") || !strcmp(command, "withdraw")) {
            if (!argument || extra) error = "invalid_arguments";
            else if (!parse_amount(argument, &amount)) error = "invalid_amount";
            else if (!strcmp(command, "deposit")) {
                if (amount > INT64_MAX - balance) error = "balance_overflow";
                else balance += amount;
            } else {
                if (amount > balance) error = "insufficient_funds";
                else balance -= amount;
            }
        } else error = "unknown_command";
        if (error) {
            failed = 1;
            report("error", error, balance);
        } else report("ok", command, balance);
    }
    if (ferror(stdin)) {
        report("error", "input_error", balance);
        return 1;
    }
    return failed ? 1 : 0;
}
